#!usr/bin/env python3

import os
import re
import shlex
import subprocess
from sys import stderr

from disc import wait_for_disc_inserted
from makemkv import MAKEMKVCON # TODO: move dependend functionality into makemkv module
from util import notify

class BaseInfo:
  '''
  Base metadata class.  Includes accessor for undefined attributes based on
  static _field_lookup member provided by subclasses.  This enables the numeric
  fields pulled from the disc to be referenced by name, such as CDATA field
  "0,2" referring to the source name
  '''
  def __init__(self, records, k, l = 2):
    self.fields = {}
    for record in records:
      index = ','.join(record[k:k+l])
      value = ','.join(record[k+l:])
      self.fields[index] = value
  
  def __getattr__(self, name: str):
    if name == 'index': 
      return self.fields['index']
    else:
      try:
        return re.sub(
          r'^"', '', re.sub(
            r'"\n?$', '', self.fields[self._field_lookup[name]]
          )
        )
      except Exception as ex:
        print('Failed to look up', name, self.fields, file=stderr)
        raise(ex)

class TOC:
  def __init__(self, print=print):
    self.lines = []
    self.source = None
    self.print=print

  def get_from_disc(self, source):
    self.print('Loading Disc TOC (this will take a while)')
    notify('Loading Disc TOC (this will take a while)')

    wait_for_disc_inserted(source, self.print)

    cmd = shlex.join([
      MAKEMKVCON, 'info', source, '--robot'
    ])

    # Load the disc TOC from makemkvcon output
    with subprocess.Popen(
      [MAKEMKVCON, 'info', source, '--robot'],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    ) as process:
      for b_line in process.stdout:
        line = b_line.decode('UTF-8').strip()
        self.lines += [line]
        if self.print != print: self.print(line)

    self.load()

  def get_from_list(self, lines):
    self.lines = lines
    self.load()

  def load(self):
    '''
    Loads disc TOC from input array of lines from `makemkvcon --robot` output
    '''
    records = [
      [line[0]] + line[1].split(',')
      for line in [
        # Safety for colons in following fields
        [line.split(':')[0], ':'.join(line.split(':')[1:])]
        for line 
        in self.lines 
        if line.startswith('CINFO')
          or line.startswith('TINFO')
          or line.startswith('SINFO')
      ]
    ]

    self.source = SourceInfo([
      record
      for record in records
      if record[0] == 'CINFO'
    ])

    self.source.add_titles(records)
    self.source.add_tracks(records)

class SourceInfo (BaseInfo):
  '''
  Source Information
  '''
  key = "CINFO"

  _field_lookup = {
    "name": "2,0",
    "name1": "2,0",
    "name2": "30,0",
    "name3": "32,0"
  }

  def __init__(self, records):
    super().__init__(records, 1)
    self.titles = []

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
  '''
  key = 'TINFO'

  _field_lookup = {
    'chapters': '8,0',
    'runtime': '9,0',
    'size': '10,0',
    'segments': '25,0',
    'segments_map': '26,0',
    'filename': '27,0'
  }

  def __init__(self, records):
    super().__init__(records, 2)
    self.tracks = []

class TrackInfo (BaseInfo):
  '''
  Track Information
  '''
  _key = 'SINFO'

  _field_lookup = {

  }

  def __init__(self, records):
    super().__init__(records, 3)

