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
from mkvtoolnix import split_mkv
import tmdb
from toc import TOC
from util import rsync, sanitize, string_to_list_int

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
    rip_all=False,
    split_segments=None,
    source_path=None,
    interface: Interface = PlaintextInterface()
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
  if (source_path is None):
    temp_dir = tempfile.mkdtemp()
    rip_path = os.path.join(temp_dir, show_name_with_id)
  else:
    interface.print_mkv("Setting temp dir to provided source path")
    temp_dir = source_path
    rip_path = os.path.join(temp_dir, show_name_with_id)

  os.makedirs(os.path.join(
    rip_path,
    season_dir, 
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print_sort(f"These titles will be given the source name of {show_name_with_id}")
    interface.print_sort(f"and copied to {dest_season_path}/{show_name} SxxExx.mkv")

    with open(os.path.join(rip_path, f'{toc.source.name}-makemkvcon.txt'), 'w') as file:
      for line in toc.lines:
        file.write(line + '\n')

    if rip_all:
      rip_disc(source, rip_path, rip_titles=['all'], interface=interface)
    else:
      rip_disc(source, rip_path, rip_titles=episode_indexes, interface=interface)
      rip_disc(source, rip_path, rip_titles=extras_indexes, interface=interface)

  def sorting_thread():
    try:
      failed_titles = []
      if features.DO_SORT:
        for i, index in enumerate(episode_indexes):
          title = toc.source.titles[int(index)]
          if split_segments:
            if features.DO_SPLIT:
              split_mkv(
                os.path.join(rip_path, title.filename), 
                os.path.join(rip_path, 'split-%d.mkv'),
                split_segments,
                interface=interface
              )
            for segment_index in range(0, len(split_segments)+1):
              try:
                  os.rename(
                    os.path.join(rip_path, f'split-{segment_index+1}.mkv'),
                    os.path.join(rip_path, season_dir, f"{show_name} S{season_number:02d}E{segment_index+first_ep:02d}.mkv")
                  )
              except FileNotFoundError as ex:
                interface.print_sort('Failed to rename segment', segment_index)
                interface.print_sort(ex)
                failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}, Segment {segment_index}\n{ex}')
            if (features.DO_CLEANUP):
              os.remove(os.path.join(rip_path, title.filename))
          else:
            try:
              os.rename(
                os.path.join(rip_path, title.filename), 
                os.path.join(rip_path, season_dir, f"{show_name} S{season_number:02d}E{i+first_ep:02d}.mkv")
              )
            except FileNotFoundError as ex:
              failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

        for index in extras_indexes:
          title = toc.source.titles[int(index)]
          try:
            os.rename(
              os.path.join(rip_path, title.filename), 
              os.path.join(rip_path, season_dir, 'extras', title.filename)
            )
          except FileNotFoundError as ex:
            failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

        if len(failed_titles) > 0:
          interface.print_sort("Some shows failed to rip or copy")
          interface.print_sort()
          for title in failed_titles:
            print(title, file=sys.stderr)
            interface.print_sort(title)
          try:
            interface.get_input("press Enter to continue or Ctrl-C to cancel")
          except KeyboardInterrupt:
            interface.print_input("Quitting...")
            sys.exit(256)

      if features.DO_COPY:
        os.makedirs(dest_season_path, exist_ok=True)
        rsync(os.path.join(rip_path), dest_path, interface=interface)

    finally:
      if features.DO_CLEANUP:
        shutil.rmtree(temp_dir)
      else:
        interface.print_sort(f"Leaving rip source at {temp_dir}")

  threading.Thread(target=sorting_thread, daemon=True).start()

  eject_disc(source, interface=interface)

def rip_show_interactive(
    source, 
    dest_path, 
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
    interface=PlaintextInterface()
  ):

  interface.print_input('Source Path', source_path)

  while True:
    # Reset per loop
    first_ep = None 
    extras_indexes = None

    wait_for_disc_inserted(source, interface)
    toc = TOC(interface=interface)

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    thread.start()

    show_name = interface.get_input('What is the name of this show?', show_name)

    results = tmdb.search('tv', show_name)
    if (id is None and len(results) > 0):
      id = results[0].id
      for result in results:
        interface.print_input(result)
      
      interface.print_input(f'These came up when searching for "{show_name}" on TMDB and the first was auto-selected.')
      interface.print_input(f'Verify at the link above or input the correct ID.')
    else:
      interface.print_input('Pre-selected ID', id)
      interface.print_input('Number of results', len(results))
      for result in results:
        interface.print_input(result)

    id = interface.get_input(f'What is the {id_key} of this show?', id)
    season_number = int(interface.get_input(f'What season is this disc?', season_number))
    first_ep = int(interface.get_input(f'What is the first episode number on this disc?', first_ep))

    interface.print_status('Waiting for TOC read to complete...')
    thread.join()

    interface.print_mkv("All Titles")
    interface.print_mkv(toc.source)

    all_indexes = [
      title.index
      for title in toc.source.titles
    ]

    episode_indexes = interface.get_input("Which titles are episodes?", value=episode_indexes)
    episode_indexes = string_to_list_int(episode_indexes)

    if len(episode_indexes) == 1:
      selected_title = toc.source.titles[episode_indexes[0]]
      interface.print_mkv(f'Segments: {selected_title.segments} Chapters: {selected_title.chapters}')
      split_segments = interface.get_input(
        f"Only one title was selected, should this be split by segment ({selected_title.segments} total)?",
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
        interface.print_mkv('Will split at chapters', split_segments)
    else: 
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
      interface.print_mkv('Ripping all titles')
      rip_all = True
    else:
      interface.print_mkv(f'Ripping main features {episode_indexes} and extras {extras_indexes}')

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
      id_key,
      rip_all=rip_all,
      split_segments=split_segments,
      source_path=source_path,
      interface=interface,
    )

    if not batch: break

  return { # Pass provided options back for batch processing
    'show_name': show_name,
    'season_number': season_number,
    'first_ep': None,
    'id': id,
    'id_key': id_key,
    'episode_indexes': None,
    'extras_indexes': None,
    'split_segments': split_segments
  }