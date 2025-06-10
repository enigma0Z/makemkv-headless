#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import threading

import logging

from sort import SortInfo, sort_titles
logger = logging.getLogger(__name__)

from disc import eject_disc, wait_for_disc_inserted
from interface import BaseInterface, PlaintextInterface, Target
from makemkv import rip_disc
from toc import TOC
from util import hms_to_seconds, rsync, sanitize, string_to_list_int

import api.src.tmdb_search.search as search
import features

def rip_movie(
    source: str, 
    dest_path: str, 
    toc: TOC,
    sort_info: SortInfo,
    rip_all=False,
    interface: BaseInterface = PlaintextInterface(),
    temp_prefix: str = None,
  ):
  '''
  `<dir>/<movie_name>/Season <season_number>/<movie_name> S<season_number>E<episode_number>.mkv`
  '''

  logger.debug(
    'rip_movie() called with args; '
    f'source: {source}, '
    f'dest_path: {dest_path}, '
    f'toc: {toc}, '
    f'sort_info: {sort_info}, '
    f'rip_all: {rip_all}, '
    f'interface: {interface}, '
    f'temp_prefix: {temp_prefix}'
  )

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  rip_path_base = tempfile.mkdtemp(prefix=temp_prefix)
  rip_path = os.path.join(rip_path_base, sort_info.path())

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print(f"These titles will be copied to {sort_info.base_path()}", target=Target.SORT)
    logger.info(f"These titles will be copied to {sort_info.base_path()}")

    with open(os.path.join(rip_path, sanitize(f'{toc.source.name}-makemkvcon.txt')), 'w') as file:
      file.writelines(toc.lines)

    if rip_all:
      rip_disc(source, rip_path, ['all'], interface=interface)
    else:
      rip_disc(source, rip_path, rip_titles=sort_info.main_indexes, interface=interface)
      rip_disc(source, rip_path, rip_titles=sort_info.extra_indexes, interface=interface)

  threading.Thread(
    kwargs={
      'toc': toc,
      'rip_path_base': rip_path_base,
      'dest_path_base': dest_path,
      'sort_info': sort_info,
      'interface': interface
    },
    target=sort_titles,
    daemon=True
  ).start()

  eject_disc(source, interface=interface)

def rip_movie_interactive(
    source, 
    dest_path, 
    batch=False,
    interface: BaseInterface = PlaintextInterface(),
    **kwargs
  ):
  logging.debug(f'called with {kwargs}')

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

    interface.print('Getting Disc Toc...', target=Target.MKV)
    thread.start()

    movie_name = interface.get_input('What is the name of this movie?', movie_name)

    results = search.search('movie', movie_name)
    if (id is None and len(results) > 0):
      id = results[0].id
      interface.print(f'\nSearch results for "{movie_name}":', target=Target.INPUT)
      interface.print(f'\nBest Match:\n{results[0]}', target=Target.INPUT)
      interface.print(f'\nAdditional Results:', target=Target.INPUT)
      for result in results[1:9]:
        interface.print(result, target=Target.INPUT)
      
    else:
      interface.print('Pre-selected ID', id, target=Target.INPUT)
      interface.print('Number of results', len(results), target=Target.INPUT)
      for result in results:
        interface.print(result, target=Target.INPUT)

    id = interface.get_input(f'What is the {id_key} of this movie?', id)

    interface.print('Waiting for TOC read to complete...', target=Target.STATUS)
    interface.title('Waiting for TOC read to complete...', target=Target.MKV)
    thread.join()

    interface.print("All Titles", target=Target.MKV)
    interface.print(toc.source, target=Target.MKV)

    logger.info('Processed table of contents')
    logger.info(toc.source)

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
      interface.print('Ripping all titles', target=Target.MKV)
      rip_all = True
    else:
      interface.print(f'Ripping main features {main_indexes} and extras {extras_indexes}', target=Target.MKV)

    sort_info = SortInfo(
      name=movie_name,
      id=id,
      id_db=id_key,
      main_indexes=main_indexes,
      extra_indexes=extras_indexes
    )

    rip_movie(
      source, 
      dest_path, 
      toc, 
      sort_info=sort_info,
      rip_all=rip_all,
      interface=interface,
      temp_prefix=kwargs['temp_prefix']
    )

    if not batch: break
  
  return {}
