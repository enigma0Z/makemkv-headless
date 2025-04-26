#!/usr/bin/env python3

import os
import shutil
import sys
import tempfile
import threading

from disc import eject_disc, wait_for_disc_inserted
from interface import Interface, PlaintextInterface, Target
from makemkv import rip_disc
from mkvtoolnix import split_mkv
from toc import TOC
from util import hms_to_seconds, rsync, sanitize, string_to_list_int

import tmdb
import features


EPISODE_LENGTH_TOLERANCE = 90

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
    interface: Interface = PlaintextInterface(),
    temp_prefix: str = None,
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
    temp_dir = tempfile.mkdtemp(prefix=temp_prefix)
    rip_path = os.path.join(temp_dir, show_name_with_id)
  else:
    interface.print("Setting temp dir to provided source path", target='mkv')
    temp_dir = source_path
    rip_path = os.path.join(temp_dir, show_name_with_id)

  os.makedirs(os.path.join(
    rip_path,
    season_dir, 
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print(f"These titles will be given the source name of {show_name_with_id}", target='sort')
    interface.print(f"and copied to {dest_season_path}/{show_name} SxxExx.mkv", target='sort')

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
        episode_number = first_ep
        # episode_indexes refers to the title number on the disk.  This may be
        # title 02, 03, 04, 05, 08, etc... for a set of sequential episodes.
        # Enumerating here transforms this unordered non-sequential list into a
        # sequential list of integers, which is why we discard title here in
        # favor of _index_
        for title_number, index in enumerate(episode_indexes):
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
                    os.path.join(rip_path, season_dir, f"{show_name} S{season_number:04d}E{episode_number:04d}.mkv")
                  )
                  episode_number += 1
              except FileNotFoundError as ex:
                interface.print('Failed to rename segment', segment_index, target='sort')
                interface.print(ex, target='sort')
                failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}, Segment {segment_index}\n{ex}')
            if (features.DO_CLEANUP):
              os.remove(os.path.join(rip_path, title.filename))
          else:
            try:
              os.rename(
                os.path.join(rip_path, title.filename), 
                os.path.join(rip_path, season_dir, f"{show_name} S{season_number:02d}E{episode_number:02d}.mkv")
              )
              episode_number += 1
            except FileNotFoundError as ex:
              failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

        for index in extras_indexes:
          title = toc.source.titles[int(index)]
          try:
            os.rename(
              os.path.join(rip_path, title.filename), 
              os.path.join(rip_path, season_dir, 'extras', f'{toc.source.name} - {title.filename}')
            )
          except FileNotFoundError as ex:
            failed_titles.append(f'{title.index}: {title.filename}, {title.runtime}\n{ex}')

        if len(failed_titles) > 0:
          interface.print("Some shows failed to rip or copy", target='sort')
          for title in failed_titles:
            print(title, file=sys.stderr)
            interface.print(title, target='sort')
          try:
            interface.get_input("press Enter to continue or Ctrl-C to cancel")
          except KeyboardInterrupt:
            interface.print("Quitting...", target='input')
            sys.exit(256)

      if features.DO_COPY:
        rsync(os.path.join(rip_path), dest_path, interface=interface)

    finally:
      if features.DO_CLEANUP:
        shutil.rmtree(temp_dir)
      else:
        interface.print(f"Leaving rip source at {temp_dir}", target='sort')

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
    interface=PlaintextInterface(),
    **kwargs,
  ):

  interface.print('Source Path', source_path, target='input')
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
      interface.print(f'\nSearch results for "{show_name}":', target='input')
      interface.print(f'\nBest Match:\n{results[0]}', target='input')
      interface.print(f'\nAdditional Results:', target='input')
      for result in results[1:9]:
        interface.print(result, target='input')
      
    else:
      interface.print('Pre-selected ID', id, target='input')
      interface.print('Number of results', len(results), target='input')
      for result in results:
        interface.print(result, target='input')

    id = interface.get_input(f'What is the {id_key} of this show?', id)
    season_number = int(interface.get_input(f'What season is this disc?', season_number))
    first_ep = int(interface.get_input(f'What is the first episode number on this disc?', next_first_ep))

    interface.print('Waiting for TOC read to complete...', target='status')
    interface.title('Waiting for TOC read to complete...', target=Target.MKV)
    thread.join()

    interface.print("All Titles", target='mkv')
    interface.print(toc.source, target='mkv')

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
      interface.print(f'Segments: {selected_title.segments} Chapters: {selected_title.chapters}', target='input')
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
        interface.print('Will split at chapters', split_segments, target='mkv')
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
      interface.print('Ripping all titles', target='mkv')
      rip_all = True
    else:
      interface.print(f'Ripping main features {episode_indexes} and extras {extras_indexes}', target='mkv')

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