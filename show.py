#!/usr/bin/env python3

import os
import re
import shutil
import sys
import tempfile
import threading

from disc import eject_disc, rip_disc
from features import DO_CLEANUP, DO_COPY, DO_RIP, DO_SORT
from toc import TOC
from util import input_with_default, rsync, sanitize, string_to_list_int

def rip_show(
    source: str, 
    dest_path: str, 
    toc: TOC,
    episode_indexes: list[int],
    extras_indexes: list[int],
    show_name: str,
    season_number: int,
    first_ep: int,
    id: str,
    id_key="tmdbid",
    rip_all=False
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''

  # For naming episodes
  show_name = sanitize(show_name) # Show files
  show_name_with_id = f"{show_name} [{id_key}-{id}]" # Show folder

  season_dir = f'Season {season_number:02d}'
  dest_season_path = os.path.join(dest_path, show_name_with_id, season_dir)

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  temp_dir = tempfile.mkdtemp()
  rip_path = os.path.join(temp_dir, show_name_with_id)

  os.makedirs(os.path.join(
    rip_path,
    season_dir, 
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    print(f"These titles will be given the source name of {show_name_with_id}")
    print(f"and copied to {dest_season_path}/{show_name} SxxExx.mkv")

    with open(os.path.join(rip_path, f'{toc.source.name}-makemkvcon.txt'), 'w') as file:
      file.writelines(toc.lines)

    if rip_all:
      rip_disc(source, rip_path, ['all'])
    else:
      rip_disc(source, rip_path, rip_titles=episode_indexes)
      rip_disc(source, rip_path, rip_titles=extras_indexes)

  def sorting_thread():
      if features.DO_SORT:
            if features.DO_SPLIT:
            if (features.DO_CLEANUP):

      for index in extras_indexes:
        title = toc.source.titles[index]
        try:
          os.rename(
            os.path.join(rip_path, title.filename), 
            os.path.join(rip_path, season_dir, 'extras', title.filename)
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

      if features.DO_COPY:
      os.makedirs(dest_season_path, exist_ok=True)
      rsync(os.path.join(rip_path), dest_path)

      if features.DO_CLEANUP:

  threading.Thread(target=sorting_thread).start()

  eject_disc(source)

def rip_show_interactive(source, dest_path, batch=False):
  show_name = None
  season_number = None
  first_ep = None
  id = None
  episode_indexes = None
  extras_indexes = None
  id_key="tmdbid"

  while True:
    # Reset per loop
    first_ep = None 
    extras_indexes = None

    toc = TOC()

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    print('Getting Disc Toc...')
    thread.start()

    show_name = input_with_default('What is the name of this show?', show_name)
    id = input_with_default(f'What is the {id_key} of this show?', id)
    season_number = int(input_with_default(f'What season is this disc?'))
    first_ep = int(input_with_default(f'What is the first episode number on this disc?', first_ep))

    print('Waiting for TOC read to complete...')
    thread.join()

    print("All Titles")
    toc.source.print()
    
    episode_indexes = input_with_default("Which titles are episodes?", value=episode_indexes)
    episode_indexes = string_to_list_int(episode_indexes)

    extras_indexes = input_with_default('Which titles are extras?', extras_indexes, lambda x: True)
    extras_indexes = string_to_list_int(extras_indexes)

    rip_show(
      source, 
      dest_path, 
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
