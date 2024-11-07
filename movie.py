#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import threading

import features

from disc import eject_disc, wait_for_disc_inserted
from interface import Interface, PlaintextInterface
from makemkv import rip_disc
import tmdb
from toc import TOC
from util import hms_to_seconds, rsync, sanitize, string_to_list_int

def rip_movie(
    source: str, 
    dest_path: str, 
    toc: TOC,
    main_indexes: list[int],
    extras_indexes: list[int],
    movie_name: str,
    id: str,
    id_key="tmdbid",
    rip_all=False,
    interface: Interface = PlaintextInterface()
  ):
  '''
  `<dir>/<movie_name>/Season <season_number>/<movie_name> S<season_number>E<episode_number>.mkv`
  '''

  # For naming episodes
  movie_name = sanitize(movie_name) # Show files
  movie_name_with_id = f"{movie_name} [{id_key}-{id}]" # Show folder

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  temp_dir = tempfile.mkdtemp()
  rip_path = os.path.join(temp_dir, movie_name_with_id)

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print_sort(f"These titles will be given the source name of {movie_name_with_id}")
    interface.print_sort(f"and copied to {dest_path}/{movie_name_with_id}/{movie_name_with_id}.mkv")

    with open(os.path.join(rip_path, f'{toc.source.name}-makemkvcon.txt'), 'w') as file:
      file.writelines(toc.lines)

    if rip_all:
      rip_disc(source, rip_path, ['all'], interface=interface)
    else:
      rip_disc(source, rip_path, rip_titles=main_indexes, interface=interface)
      rip_disc(source, rip_path, rip_titles=extras_indexes, interface=interface)

  def sorting_thread():
    failed_titles = []
    if features.DO_SORT:
      for index in main_indexes:
        title = toc.source.titles[int(index)]
        try:
          os.rename(
            os.path.join(rip_path, title.filename), 
            os.path.join(rip_path, f"{movie_name_with_id} - {index}.mkv")
          )
        except FileNotFoundError as ex:
          failed_titles.append(title)

      for index in extras_indexes:
        title = toc.source.titles[int(index)]
        try:
          os.rename(
            os.path.join(rip_path, title.filename), 
            os.path.join(rip_path, 'extras', title.filename)
          )
        except FileNotFoundError as ex:
          failed_titles.append(title)

      if len(failed_titles) > 0:
        interface.print_sort("Some failed to rip or copy")
        interface.print_sort()
        for title in failed_titles:
          interface.print_sort(f'{title.index}: {title.filename}, {title.runtime}')
        interface.print_sort("press Enter to continue or Ctrl-C to cancel")
        try:
          interface.get_input()
        except KeyboardInterrupt:
          interface.print_input("Quitting...")
          sys.exit(256)

    if features.DO_COPY:
      os.makedirs(dest_path, exist_ok=True)
      rsync(rip_path, dest_path, _print=print_sort)

    if features.DO_CLEANUP:
      shutil.rmtree(temp_dir)
    else:
      interface.print_sort(f"Leaving rip source at {temp_dir}")

  threading.Thread(target=sorting_thread).start()

  eject_disc(source)

def rip_movie_interactive(
    source, 
    dest_path, 
    batch=False,
    interface: Interface = PlaintextInterface(),
  ):
  movie_name = None
  id = None
  main_indexes = None
  extras_indexes = None
  id_key="tmdbid"

  while True:
    wait_for_disc_inserted(source)
    extras_indexes = None # Reset per loop

    toc = TOC(interface=interface)

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    interface.print_mkv('Getting Disc Toc...')
    thread.start()

    movie_name = interface.get_input('What is the name of this movie?', movie_name)

    results = tmdb.search('movie', movie_name)
    if (id is None and len(results) > 0):
      id = results[0].id
      for result in results:
        interface.print_mkv(result)
      
      interface.print_input(f'These came up when searching for "{movie_name}" on TMDB and the first was auto-selected.')
      interface.print_input(f'Verify at the link above or input the correct ID.')
    else:
      interface.print_input('Pre-selected ID', id)
      interface.print_input('Number of results', len(results))
      for result in results:
        interface.print_mkv(result)

    id = interface.get_input(f'What is the {id_key} of this movie?', id)

    interface.print_status('Waiting for TOC read to complete...')
    thread.join()

    interface.print_mkv("All Titles")
    interface.print_mkv(toc.source)

    all_indexes = [
      title.index
      for title in toc.source.titles
    ]

    longest_title = sorted(
      toc.source.titles, 
      key=lambda title: hms_to_seconds(title.runtime),
      reverse=True
    )[0]

    main_indexes = [longest_title.index]
    
    main_indexes = interface.get_input("Which titles are the main feature?", value=main_indexes)
    main_indexes = string_to_list_int(main_indexes)

    extras_indexes = [
      title.index
      for title in toc.source.titles
      if title.index not in main_indexes
    ]

    extras_indexes = interface.get_input('Which titles are extras?', extras_indexes, lambda x: True)
    extras_indexes = string_to_list_int(extras_indexes)

    rip_all = False
    if(sorted(all_indexes) == sorted(main_indexes + extras_indexes)):
      interface.print_mkv('Ripping all titles')
      rip_all = True
    else:
      interface.print_mkv(f'Ripping main features {main_indexes} and extras {extras_indexes}')

    rip_movie(
      source, 
      dest_path, 
      toc, 
      main_indexes, 
      extras_indexes, 
      movie_name, 
      id, 
      id_key,
      rip_all=rip_all,
      interface=interface,
    )

    if not batch: break
  
  return {}
