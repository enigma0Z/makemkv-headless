#!/usr/bin/env python3

import threading

import logging

from src.interface.base_interface import BaseInterface
from src.interface.plaintext_interface import PlaintextInterface
from src.rip_titles.rip_titles import rip_titles
from src.sort import ShowInfo, SortInfo
from src.disc import wait_for_disc_inserted
from src.toc import TOC
from src.util import hms_to_seconds, string_to_list_int

from src.tmdb import search

logger = logging.getLogger(__name__)

EPISODE_LENGTH_TOLERANCE = 90

def rip_movie_interactive(
    source, 
    destination, 
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

    rip_titles(
      source, 
      destination, 
      toc, 
      sort_info=sort_info,
      rip_all=rip_all,
      interface=interface,
      temp_prefix=kwargs['temp_prefix']
    )

    if not batch: break
  
  return {}

def rip_show_interactive(
    source, 
    destination, 
    show_name = None,
    season_number = None,
    first_ep = None,
    id = None,
    id_key="tmdbid",
    episode_indexes = None,
    extras_indexes = None,
    split_segments = True,
    batch=False, 
    interface=PlaintextInterface(),
    **kwargs,
  ):

  next_first_ep = first_ep

  while True:
    wait_for_disc_inserted(source, interface)
    toc = TOC(interface=interface)

    thread = threading.Thread(target=toc.get_from_disc, args=[source])

    thread.start()

    show_name = interface.get_input('What is the name of this show?', show_name)

    results = search.search('tv', show_name)
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

    rip_titles(
      source, 
      destination, 
      toc, 
      sort_info=sort_info,
      rip_all=rip_all,
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