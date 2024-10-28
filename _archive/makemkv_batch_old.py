#!/usr/bin/env python3

import os
import shutil
import shlex
import re
import sys
import threading
import subprocess

from argparse import ArgumentParser
from time import sleep
from tempfile import TemporaryDirectory

MAKEMKVCON="/Applications/MakeMKV.app/Contents/MacOS/makemkvcon"

## Global feature flags

DO_RIP=True
DO_SORT=True

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
            r'"\n$', '', self.fields[self._field_lookup[name]]
          )
        )
      except Exception as ex:
        print('Failed to look up', name, self.fields)
        raise(ex)

class TOC:
  def __init__(self):
    self.lines = []
    self.source = None

  def get_from_disc(self, source):
    print('Loading Disc TOC (this will take a while)')
    notify('Loading Disc TOC (this will take a while)')

    wait_for_disc_inserted(source)

    cmd = shlex.join([
      MAKEMKVCON, 'info', source, '--robot'
    ])

    # Load the disc TOC from makemkvcon output
    self.lines = os.popen(cmd).readlines()
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
        self.titles[-1].fields['index'] = title_number

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

  def print(self):
    print(self.name)
    for title in self.titles:
      print(f'{title.index} - {title.runtime}, {title.filename}')

class TitleInfo (BaseInfo):
  '''
  Title Information
  '''
  key = 'TINFO'

  _field_lookup = {
    'runtime': '9,0',
    'size': '10,0',
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

def grep(term, lines):
  return True in [ term.casefold() in line.casefold() for line in lines ]

def disc_inserted(source):
  if (source.startswith('dev')):
    device = source.split(':')[1]
    return not grep('could not find disk', os.popen(shlex.join(['diskutil', 'info', device]) + " 2>&1").readlines())
  elif (source.startswith('disc')):
    print("WARNING: makemkvcon index and drutil index do not always line up, this mode is buggy and should be avoided")
    drutil_index = int(source.split(':')[1]) + 1
    return not grep('please insert', os.popen(shlex.join(['drutil', '-drive', str(drutil_index), 'discinfo'])).readlines())

def wait_for_disc_inserted(source):
  if not disc_inserted(source):
    print(f'Please insert a disc into {source}')
    notify(f'Please insert a disc into {source}')
  while not disc_inserted(source):
    sleep(1)

def eject_disc(source):
  if (source.startswith('dev')):
    device = source.split(':')[1]
    return os.popen(shlex.join(['diskutil', 'eject', device]))
  elif (source.startswith('disc')):
    print("WARNING: makemkvcon index and drutil index do not always line up, this mode is buggy and should be avoided")
    drutil_index = int(source.split(':')[1]) + 1
    os.system(shlex.join([ 'drutil', '-drive', str(drutil_index), 'eject' ]))

def hms_to_seconds(time):
  [hours, minutes, seconds] = [int(v) for v in time.split(':')]
  hours *= 60 * 60
  minutes *= 60
  return hours + minutes + seconds

def notify(message):
  os.popen(shlex.join([
    'osascript', '-e',
    f'display notification "{message}" with title "Disc Backup"'
  ]))

def rsync(source, dest):
  # Put output files into their final destinations if the rip was done locally
  print(f'Copying local rip from {source} to {dest}')
  notify(f'Copying local rip to {dest}')
  subprocess.Popen([
    'rsync', '-av',
    f'{source}', dest
  ]).wait()

def sanitize(value: str): # Strips out non alphanumeric characters and replaces with "_"
  return re.sub(r'[^\w]', '_', value.lower())

def string_to_list(_input):
  if (type(_input) is list):
    return _input

  new_list = [
    v 
    for v 
    in re.sub(r'[^,\d-]', '', _input).split(',')
    if v != ''
  ]

  for index, value in enumerate(new_list):
    if '-' in value:
      start, end = [int(v) for v in value.split('-')]
      new_list.remove(value)
      for inner_index, value in enumerate(range(start, end + 1)):
        new_list.insert(index + inner_index, str(value))

  return new_list

def input_with_default(
    prompt, 
    validation = lambda v: v != '' and v is not None, 
    value=None
  ):
  while True:
    _input = input(f'{prompt}\n({value})> ')
    if validation(_input):
      return _input
    elif validation(value):
      return value

def rip_disc(
    source, 
    dest,
    rip_titles=['all']
  ):
  notify(f'Backing up {source} to {dest}')
  print(f'Backing up {source} to {dest}')

  wait_for_disc_inserted(source)

  # Do the actual rip + eject the disc when done
  for rip_title in rip_titles:
    print(f'Ripping title {rip_title}')
    notify(f'Ripping title {rip_title}')
    # os.system(shlex.join([ MAKEMKVCON, 'mkv', source, rip_title, dest]))
    subprocess.Popen([ MAKEMKVCON, 'mkv', source, rip_title, dest]).wait()

def rip_movie(
    source, 
    dest_dir, 
    toc: TOC,
    movie_indexes: list[int],
    extras_indexes: list[int],
    movie_name: str,
    id: str,
    id_key="imdbid"):
  '''
  If there is more than one title of the same highest length, both will be put
  in the same directory with their index in the TOC as iterators, i.e.

  `<dir>/<toc.fields.name> [<id_key>-<id>] - <index>.mkv`
  '''

  movie_name = sanitize(movie_name)
  movie_name += f" [{id_key}-{id}]"

  print(f"These titles will be copied to {dest_dir}/{movie_name}")

  try:
    # Set rip dir to a temporary file location for extraction to enable more
    # stable rips when the destination is a network location
    temp_dir = TemporaryDirectory()
    rip_dir = os.path.join(temp_dir.name, movie_name)
    os.makedirs(os.path.join(temp_dir.name, movie_name,  'extras'), exist_ok=True)

    with open(os.path.join(rip_dir, f'makemkvcon.txt'), 'w') as file:
      file.writelines(toc.lines)

    rip_disc(source, rip_dir)

    failed_titles = []
    for title in [title for title in toc.source.titles if title.index in movie_indexes]:
      try:
        os.rename(
          os.path.join(rip_dir, title.filename), 
          os.path.join(rip_dir, f"{movie_name} - {title.index}.mkv") #TODO: Better differentiator here for the index
        )
      except FileNotFoundError as ex:
        failed_titles.append(title)

    for title in [
      title 
      for title
      in toc.source.titles
      if title.index in extras_indexes
    ]:
      try:
        os.rename(
          os.path.join(rip_dir, title.filename),
          os.path.join(rip_dir, 'extras', title.filename)
        )
      except FileNotFoundError as ex:
        failed_titles.append(title)

    for title in [
      title for title
      in toc.source.titles
      if title.index not in extras_indexes
      and title.index not in movie_indexes
    ]:
      try:
        os.remove( os.path.join(rip_dir, title.filename))
      except FileNotFoundError:
        print("Could not clean up", os.path.join(rip_dir, title.filename))

    if len(failed_titles) > 0:
      print("Some failed to rip or copy")
      print()
      for title in failed_titles:
        print(f'{title.index}: {title.filename}, {title.runtime}')

    rsync(os.path.join(rip_dir), dest_dir)

  finally:
    temp_dir.cleanup()

def interactive_rip_movie(source, dest_dir, batch=False):
  while True:
    toc = TOC()
    toc.get_from_disc(source)
    
    titles_by_length = sorted(toc.source.titles, key = lambda title: hms_to_seconds(title.runtime), reverse=True)
    movie_index = [
      title.index
      for title
      in toc.source.titles
      if title.runtime == titles_by_length[0].runtime
    ]

    extras_index = [
      title.index 
      for title 
      in toc.source.titles 
      if title.index not in movie_index
    ]
  
    print("All Titles")
    toc.source.print()

    movie_name = input_with_default("What is the name of this movie?", value=toc.source.name)

    id = input_with_default('What is the IMDB ID of this movie?')

    movie_index = input_with_default("Which title(s) are the main movie?", value=movie_index)
    movie_index = string_to_list(movie_index)

    extras_index = input_with_default("Which title(s) are extra features?", value=extras_index)
    extras_index = string_to_list(extras_index) 

    rip_movie(
      source, dest_dir, toc, movie_index, extras_index, movie_name, id
    )

def rip_show(
    source: str, 
    dest_dir: str, 
    toc: TOC,
    episode_indexes: list[int],
    extras_indexes: list[int],
    show_name: str,
    season_number: int,
    first_ep: int,
    id: str,
    id_key="tmdbid"
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''

  show_name = re.sub(r'[^\w]', '_', show_name.lower())
  source_name = show_name
  if (id is not None):
    source_name += f" [{id_key}-{id}]"

  season_dir = f'Season {season_number:02d}'
  season_path = f'{dest_dir}/{source_name}/{season_dir}'

  if (DO_RIP):
    print(f"These titles will be given the source name of {source_name}")
    print(f"and copied to {season_path}/{show_name} SxxExx.mkv")

  condition = threading.Condition()

  def rip_thread():
    try:
      with condition:
        # Set rip dir to a temporary file location for extraction to enable more
        # stable rips when the destination is a network location
        temp_dir = TemporaryDirectory()
        rip_dir = os.path.join(temp_dir.name, source_name)
        os.makedirs(os.path.join(
          temp_dir.name,
          source_name,  
          season_dir,
          'extras'
        ), exist_ok=True)

        if DO_RIP:
          with open(os.path.join(rip_dir, f'{toc.source.name}-makemkvcon.txt'), 'w') as file:
            file.writelines(toc.lines)

          rip_disc(source, rip_dir, rip_titles=episode_indexes)
          rip_disc(source, rip_dir, rip_titles=extras_indexes)

        failed_titles = []
        if DO_SORT:
          for index in episode_indexes:
            try:
              os.rename(
                os.path.join(rip_dir, toc.source.titles[int(index)].filename), 
                os.path.join(rip_dir, season_dir, f"{show_name} S{season_number:02d}E{int(index)+first_ep:02d}.mkv")
              )
            except FileNotFoundError as ex:
              failed_titles.append(title)

          for index in extras_indexes:
            try:
              os.rename(
                os.path.join(rip_dir, toc.source.titles[int(index)].filename), 
                os.path.join(rip_dir, season_dir, 'extras', toc.source.titles[int(index)].filename)
              )
            except FileNotFoundError as ex:
              failed_titles.append(title)

        if len(failed_titles) > 0:
          print("Some failed to rip or copy")
          print()
          for title in failed_titles:
            print(f'{title.index}: {title.filename}, {title.runtime}')
          print("press Enter to continue or Ctrl-C to cancel")
          try:
            input()
          except KeyboardInterrupt:
            print("Quitting...")
            sys.exit(256)

        condition.notify()

      os.makedirs(season_path, exist_ok=True)
      rsync(os.path.join(rip_dir), dest_dir)

    finally:
      temp_dir.cleanup()

  thread = threading.Thread(target=rip_thread)
  with condition:
    print("Starting ripping thread")
    thread.start()
    print("Waiting on disk use to be completed")
    condition.wait()

  eject_disc()

def input_show_parameters(show_name=None, season_number=None, id=None, id_key="tmdbid", interactive=True):
  _input = input(f'What is the name of this show?\n({show_name})> ')
  if _input != '':
    show_name = _input
  elif show_name is None:
    raise ValueError('No show name specified')

  _input = input(f'What is the {id_key} of this show?\n({id})> ')
  if _input != '':
    id = _input
  elif id is None:
    raise ValueError(f'No {id_key} ID number specified')

  _input = input(f'What season is this disc\n({season_number})> ')
  if _input != '':
    season_number = int(_input)
  elif season_number is None:
    raise ValueError('No season number specified')

  _input = input(f'What is the first episode number on this disc?\n(None)> ')
  if _input != '':
    first_ep = int(_input)
  else:
    raise ValueError('No first episode number specified')
  
  return [show_name, season_number, first_ep, id]

def interactive_rip_show(source, dest_dir, batch=False):
  show_name = None
  season_number = None
  first_ep = None
  id = None
  episode_indexes = None
  extras_indexes = None
  id_key="tmdbid"

  while True:
    extras_indexes = None # Reset per loop

    toc = TOC()

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    print('Getting Disc Toc...')
    thread.start()

    [show_name, season_number, first_ep, id] = input_show_parameters(
      show_name, season_number, id, id_key
    )

    print('Waiting for TOC read to complete...')
    thread.join()

    print("All Titles")
    toc.source.print()
    
    episode_indexes = input_with_default("Which titles are episodes?", value=episode_indexes)
    episode_indexes = string_to_list(episode_indexes)

    extras_indexes = input_with_default('Which titles are extras?', value=extras_indexes)
    extras_indexes = string_to_list(extras_indexes)

    rip_show(
      source, 
      dest_dir, 
      toc, 
      episode_indexes, 
      extras_indexes, 
      show_name, 
      season_number, 
      first_ep, 
      id, 
      id_key
    )

    if not batch: break

if __name__=='__main__':
  parser = ArgumentParser()
  parser.add_argument('source', default="disc:0")
  parser.add_argument('dest_dir')
  parser.add_argument('--mode', action='store', default='movies')
  parser.add_argument('--batch', action='store_true')
  parser.add_argument('--imdbid', action='store', default=None)
  parser.add_argument('--tmdbid', action='store', default=None)
  parser.add_argument('--skip-sort', action='store_true')
  parser.add_argument('--skip-rip', action='store_true')

  opts = parser.parse_args(sys.argv[1:])

  DO_SORT = not opts.skip_sort
  DO_RIP = not opts.skip_rip

  if opts.mode.startswith('movie'):
    if opts.batch:
      interactive_rip_movie(opts.source, opts.dest_dir, batch=True)
    else:
      interactive_rip_movie(opts.source, opts.dest_dir, batch=False)
  elif opts.mode.startswith('show'):
    if opts.batch:
      interactive_rip_show(opts.source, opts.dest_dir, batch=True)
    else:
      # TODO: If params provided to rip show immediately do it
      # Need source, dest, episode indexes, extras indexes, show name, season number, first ep, tmdb id
      # Else rip a single disc (i.e. not batch mode) interactively
      interactive_rip_show(opts.source, opts.dest_dir, batch=False)
