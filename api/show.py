#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import threading

import logging
logger = logging.getLogger(__name__)

from sort import ShowInfo, SortInfo, sort_titles

from disc import eject_disc, wait_for_disc_inserted
from interface import Interface, PlaintextInterface, Target
from makemkv import rip_disc
from mkvtoolnix import split_mkv
from toc import TOC
from util import hms_to_seconds, rsync, sanitize, string_to_list_int

import tmdb
import features


EPISODE_LENGTH_TOLERANCE = 90

      # source, 
      # dest_path_base, 
      # toc, 
      # sort_info=sort_info,
      # rip_all=rip_all,
      # source_path=source_path,
      # interface=interface,
      # **kwargs,

def rip_show(
    source: str, 
    dest_path: str, 
    toc: TOC,
    sort_info: SortInfo,
    rip_all=False,
    source_path=None,
    interface: Interface = PlaintextInterface(),
    temp_prefix: str = None,
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''
  logger.debug(
    'rip_show() called with args', 
    f'source: {source}',
    f'dest_path: {dest_path}',
    f'toc: {toc}',
    f'sort_info: {sort_info}',
    f'rip_all: {rip_all}',
    f'source_path: {source_path}',
    f'interface: {interface}',
    f'temp_prefix: {temp_prefix}'
  )

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  if (source_path is None):
    rip_path_base = tempfile.mkdtemp(prefix=temp_prefix)
    rip_path = os.path.join(rip_path_base, sort_info.path())
  else:
    interface.print("Setting temp dir to provided source path", target=Target.MKV)
    rip_path_base = source_path
    rip_path = os.path.join(rip_path_base, sort_info.path())

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print(f"These titles will be copied to {sort_info.base_path()}", target=Target.SORT)

    with open(os.path.join(rip_path, f'{toc.source.name}-makemkvcon.txt'), 'w') as file:
      for line in toc.lines:
        file.write(line + '\n')

    if rip_all:
      rip_disc(source, rip_path, rip_titles=['all'], interface=interface)
    else:
      rip_disc(source, rip_path, rip_titles=sort_info.episode_indexes, interface=interface)
      rip_disc(source, rip_path, rip_titles=sort_info.extras_indexes, interface=interface)

  # Run sort and copy in its own thread
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

def rip_show_interactive(
    source, 
    dest_path_base, 
    show_name = None,
    season_number = None,
    first_ep = None,
    id = None,
    id_key="tmdbid",
    episode_indexes = None,
    extras_indexes = None,
    split_segments = True,
    batch=False, 
    source_path=None,
    interface=PlaintextInterface(),
    **kwargs,
  ):

  interface.print('Source Path', source_path, target=Target.INPUT)
  next_first_ep = first_ep

  while True:
    wait_for_disc_inserted(source, interface)
    toc = TOC(interface=interface)

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    thread.start()

    show_name = interface.get_input('What is the name of this show?', show_name)

    results = tmdb.search('tv', show_name)
    if (id is None and len(results) > 0):
      id = results[0].id
      interface.print(f'\nSearch results for "{show_name}":', target=Target.INPUT)
      interface.print(f'\nBest Match:\n{results[0]}', target=Target.INPUT)
      interface.print(f'\nAdditional Results:', target=Target.INPUT)
      for result in results[1:9]:
        interface.print(result, target=Target.INPUT)
      
    else:
      interface.print('Pre-selected ID', id, target=Target.INPUT)
      interface.print('Number of results', len(results), target=Target.INPUT)
      for result in results:
        interface.print(result, target=Target.INPUT)

    id = interface.get_input(f'What is the {id_key} of this show?', id)
    season_number = int(interface.get_input(f'What season is this disc?', season_number))
    first_ep = int(interface.get_input(f'What is the first episode number on this disc?', next_first_ep))

    interface.print('Waiting for TOC read to complete...', target=Target.STATUS)
    interface.title('Waiting for TOC read to complete...', target=Target.MKV)
    thread.join()

    interface.print("All Titles", target=Target.MKV)
    interface.print(toc.source, target=Target.MKV)

    all_indexes = [
      title.index
      for title in toc.source.titles
    ]

    sorted_titles = sorted(
      toc.source.titles, 
      key=lambda title: hms_to_seconds(title.runtime),
      reverse=True
    )

    # Catcher for if there's one long title with all the eps
    for i in range(0, 2):
      episode_indexes = [
        title.index
        for title in toc.source.titles
        if hms_to_seconds(title.runtime) > hms_to_seconds(sorted_titles[i].runtime) - EPISODE_LENGTH_TOLERANCE
        and hms_to_seconds(title.runtime) < hms_to_seconds(sorted_titles[i].runtime) + EPISODE_LENGTH_TOLERANCE
      ]

      try:
        if len(episode_indexes) > 1: break # Break if we found more than one ep
      except TypeError:
        pass # TypeError if len() fails

    episode_indexes = interface.get_input("Which titles are episodes?", value=episode_indexes)
    episode_indexes = string_to_list_int(episode_indexes)

    if len(episode_indexes) == 1:
      selected_title = toc.source.titles[episode_indexes[0]]
      interface.print(f'Segments: {selected_title.segments} Chapters: {selected_title.chapters}', target=Target.INPUT)
      split_segments = interface.get_input(
        f"Should this be split by chapter or segment?",
        split_segments,
        lambda v: 
          v.casefold() in ['true', 'false', 'yes', 'no', 'y', 'n']
          or type(v) is bool
      )

      if type(split_segments) is str:
        if split_segments.casefold() in ['true', 'yes', 'y']:
          split_segments = True
        elif split_segments.casefold() in ['false', 'no', 'n']:
          split_segments = False

      if (split_segments):
        chapter_count = int(selected_title.chapters)
        segment_count = int(selected_title.segments)
        episode_count = int(interface.get_input('How many episodes are on this disc?', segment_count, lambda x: int(x)))
        chapters_per_segment = chapter_count / episode_count
        chapters_per_segment = int(interface.get_input('How many chapters per episode should the final file be split into?', chapters_per_segment, lambda x: int(x)))

        # +1 for mkvmerge
        # which indexes on 0, but takes the chapter number at which to split by the _START_
        # We then take all but the last index of the result since the last start point will be a chapter that does not exist
        split_segments = [v + chapters_per_segment + 1 for v in range(0, chapter_count, chapters_per_segment)][0:-1]
        interface.print('Will split at chapters', split_segments, target=Target.MKV)
        next_first_ep = first_ep + len(split_segments) + 1
    else: 
      next_first_ep = first_ep + len(episode_indexes)
      interface.print('The next first episode will be', next_first_ep, target=Target.INPUT)
      split_segments = False

    extras_indexes = [
      title.index
      for title in toc.source.titles
      if title.index not in episode_indexes
    ]

    extras_indexes = interface.get_input('Which titles are extras?', extras_indexes, lambda x: True)
    extras_indexes = string_to_list_int(extras_indexes)

    rip_all = False
    if(sorted(all_indexes) == sorted(episode_indexes + extras_indexes)):
      interface.print('Ripping all titles', target=Target.MKV)
      rip_all = True
    else:
      interface.print(f'Ripping main features {episode_indexes} and extras {extras_indexes}', target=Target.MKV)

    sort_info = ShowInfo(
      name=show_name,
      id=id,
      id_db=id_key,
      main_indexes=episode_indexes,
      extra_indexes=extras_indexes,
      split_segments=split_segments,
      season_number=season_number,
      first_episode=first_ep
    )

    rip_show(
      source, 
      dest_path_base, 
      toc, 
      sort_info=sort_info,
      rip_all=rip_all,
      source_path=source_path,
      interface=interface,
      **kwargs,
    )

    if not batch: break

  return { # Pass provided options back for batch processing
    'show_name': show_name,
    'season_number': season_number,
    'first_ep': next_first_ep,
    'id': id,
    'id_key': id_key,
    'episode_indexes': None,
    'extras_indexes': None,
    'split_segments': split_segments
  }