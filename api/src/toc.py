#!usr/bin/env python3

from json import dumps
import re
import subprocess
from sys import stderr

import logging

logger = logging.getLogger(__name__)

from src.config import CONFIG
from src.json_serializable import JSONSerializable
from src.interface import PlaintextInterface, Target
from src.interface.message import build_message

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

class TOC(JSONSerializable):
  def __init__(self, interface=PlaintextInterface()):
    self.lines = []
    self.source = None
    self.interface=interface

  def __getitem__(self, item):
    if item == "lines":
      return self.lines
    elif item == "source":
      return self.source

  def get_from_disc(self, source):

    self.interface.print('Loading disc TOC', target=Target.MKV)

    # Load the disc TOC from makemkvcon output
    with subprocess.Popen(
      [CONFIG.makemkvcon_path, '--noscan', '--robot', 'info', source],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    ) as process:
      for b_line in process.stdout:
        line = b_line.decode('UTF-8').strip()
        self.lines += [line]
        self.interface.send(build_message(raw=line))

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

class BaseInfo(JSONSerializable):
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
    self.fields = {}
    for record in records:
      index = ','.join(record[key_start:key_start+key_length])
      value = ','.join(record[key_start+key_length:])
      self.fields[index] = value
  
  def __getattr__(self, name: str):
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
        logger.debug(f"Could not find key {name} in fields, {ex}")
        return None

  def __getitem__(self, item: str):
    if item in self.__dict__: 
      return self.__dict__[item]
    else:
      return self.__getattr__(item)

  def json_encoder(self):
    '''
    Translate the auto-field work that __getattr__ does to pseudo attributes 
    that are returned in the JSON stream
    '''
    logger.debug('BaseInfo.json_encoder()')
    field_values = { 
      key: value
      for key, value in [ 
        (key, self.__getattr__(key))
        for key in self._field_lookup.keys()
      ]
      if value != None
    }
    return {**self.__dict__, **field_values}


class SourceInfo(BaseInfo):
  '''
  Source Information

  Example: `CINFO:2,0,"STARGATE_SG1_SEASON_10_D5_US"`
  '''
  key = "CINFO"

  _field_lookup = {
    "name": "2,0",
    "name1": "2,0",
    "name2": "30,0",
    "name3": "32,0",
    "media": "1,6206"
  }

  def __init__(self, records):
    super().__init__(records, 1)
    self.titles = []

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

class TitleInfo (BaseInfo):
  '''
  Title Information
  Example - TINFO:7,30,0,"2 chapter(s) , 44.9 MB (A1)"
  '''
  key = 'TINFO'

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

class TrackInfo (BaseInfo):
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

