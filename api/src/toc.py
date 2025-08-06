#!usr/bin/env python3

from functools import lru_cache
from json import dumps
import re
import subprocess

from pydantic import PrivateAttr

from src.config import CONFIG
from src.interface import get_interface
from src.interface.base_interface import BaseInterface
from src.interface.target import Target
from src.interface.plaintext_interface import PlaintextInterface

import logging

from src.models.socket import mkv_message_from_raw
from src.models.toc import BaseInfoModel, SourceInfoModel, TOCModel, TitleInfoModel, TrackInfoModel
logger = logging.getLogger(__name__)


def format_records(lines):
  return [
    [line[0]] + line[1].split(',')
    for line in [
      # Safety for colons in following fields
      [line.split(':')[0], ':'.join(line.split(':')[1:])]
      for line 
      in lines 
      if line.startswith('CINFO')
        or line.startswith('TINFO')
        or line.startswith('SINFO')
    ]
  ]

class TOC(TOCModel):
  _interface: BaseInterface = PrivateAttr(default_factory=get_interface)

  def __getitem__(self, item):
    if item == "lines":
      return self.lines
    elif item == "source":
      return self.source

  def get_from_disc(self, source):
    self._interface.print('Loading disc TOC', target=Target.MKV)

    # Load the disc TOC from makemkvcon output
    with subprocess.Popen(
      [CONFIG.makemkvcon_path, '--noscan', '--robot', 'info', source],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    ) as process:
      for b_line in process.stdout:
        line = b_line.decode('UTF-8').strip()
        self.lines += [line]
        self._interface.send(mkv_message_from_raw(line))

    self.load()

  def get_from_list(self, lines):
    self.lines = lines
    self.load()

  def load(self):
    '''
    Loads disc TOC from input array of lines from `makemkvcon --robot` output
    '''
    records = format_records(self.lines)

    self.source = SourceInfo([
      record
      for record in records
      if record[0] == 'CINFO'
    ])

    self.source.add_titles(records)
    self.source.add_tracks(records)

  def json_encoder(self):
    return {
      'source': self.source
    }

class BaseInfo(BaseInfoModel):
  '''
  Base metadata class.  Includes accessor for undefined attributes based on
  static _field_lookup member provided by subclasses.  This enables the numeric
  fields pulled from the disc to be referenced by name, such as CDATA field
  "0,2" referring to the source name

  Records are formatted like this: <IDENTIFIER>:<INDEXES>?:<IDENTIFIER>:<DATA>

  <INDEXES> are an optional list of indexes for which item in the list it this
  is (if applicable), followed by the two field identifier for the data type.
  `key_start` identifies where in <INDEXES> the field identifier digits start.

  It's all hierarchical, so Sources ("CINFO") have Titles ("TINFO"), which have
  Tracks or Streams ("SINFO"), and as you descend the layers, an additional
  index is added on.  SINFO 7,2 means this is stream 2 of title 7, for instance.
  '''
  _field_lookup = {}

  def __init__(self, records, key_start, key_length = 2):
    data = {}
    fields: dict[str, str] = {}
    for record in records:
      index = ','.join(record[key_start:key_start+key_length])
      value = ','.join(record[key_start+key_length:])
      fields[index] = value

    super().__init__(fields=fields)

    for name, key in self._field_lookup.items():
      if key in self.fields:
        self.__dict__[name] = re.sub( # Strip leading and trailing quotes off if they exist
          r'^"', '', re.sub(
            r'"\n?$', '', self.fields[key]
          )
        )

  
  def lookup_field(self, name: str):
    if name == 'index': 
      return self.fields['index']
    else:
      try:
        return re.sub( # Strip leading and trailing quotes off if they exist
          r'^"', '', re.sub(
            r'"\n?$', '', self.fields[self._field_lookup[name]]
          )
        )
      except Exception as ex:
        return None

  def json_encoder(self):
    '''
    Translate the auto-field work that __getattr__ does to pseudo attributes 
    that are returned in the JSON stream
    '''
    field_values = { 
      key: value
      for key, value in [ 
        (key, self.__getattr__(key))
        for key in self._field_lookup.keys()
      ]
      if value != None
    }
    return {**self.__dict__, **field_values}


class SourceInfo(SourceInfoModel, BaseInfo):
  '''
  Source Information

  Example: `CINFO:2,0,"STARGATE_SG1_SEASON_10_D5_US"`
  '''
  _key = "CINFO"

  _field_lookup = {
    "name": "2,0",
    "name1": "2,0",
    "name2": "30,0",
    "name3": "32,0",
    "media": "1,6206"
  }

  def __init__(self, records):
    super().__init__(records, 1)

  def __str__(self):
    return f'SourceInfo({self.media}: {self.name})'

  def add_titles(self, records):
      title_numbers = []
      for title in [record for record in records if record[0] == 'TINFO']:
        if title[1] not in title_numbers:
          title_numbers.append(title[1])

      for title_number in title_numbers:
        self.titles.append(TitleInfo([
          record for record in records
          if record[0] == 'TINFO' and record[1] == title_number
        ]))
        self.titles[-1].fields['index'] = int(title_number)

  def add_tracks(self, records):
    for title_number in range(0, len(self.titles)):
      track_numbers = []
      for track in [
        record for record in records
        if record[0] == 'SINFO' and record[1] == str(title_number)
      ]:
        if track[2] not in track_numbers:
          track_numbers.append(track[2])
        
      for track in track_numbers:
        self.titles[title_number].tracks.append(TrackInfo([
          record for record in records
          if record[0] == 'SINFO' 
          and record[1] == str(title_number)
          and record[2] == track
        ]))
        self.titles[title_number].tracks[-1].fields['index'] = track

  def __str__(self):
    lines = [self.name]
    for title in self.titles:
      lines += [f'{title.index} - {title.runtime}, {title.filename}']

    return '\n'.join(lines)

class TitleInfo(TitleInfoModel, BaseInfo):
  '''
  Title Information
  Example - TINFO:7,30,0,"2 chapter(s) , 44.9 MB (A1)"
  '''
  _key = 'TINFO'

  _field_lookup = {
    'chapters': '8,0',
    'runtime': '9,0',
    'size': '10,0',
    'segments': '25,0',
    'segments_map': '26,0',
    'filename': '27,0',
    'summary': '30,0'
  }

  def __init__(self, records):
    super().__init__(records, 2)
    self.tracks = []

  def __str__(self):
    return f'{self.runtime} - {self.filename} - {self.summary}'

class TrackInfo(TrackInfoModel, BaseInfo):
  '''
  Track Information
  Example - SINFO:7,2,3,0,"eng"
  '''
  _key = 'SINFO'

  _field_lookup = {
    'stream_type': '1,6201',
    'stream_format': '5,0',
    'stream_conversion_type': '42,5088',
    'stream_bitrate': '13,0',
    'stream_language_code': '3,0',
    'stream_language': '4,0',
    'stream_detail': '30,0',

    'audio_format': '2,5091',

    'video_resolution': '19,0',
    'video_aspect_ratio': '20,0',
    'video_framerate': '21,0'
  }

  def __init__(self, records):
    super().__init__(records, 3)

