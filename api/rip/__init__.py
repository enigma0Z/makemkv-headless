#!/usr/bin/env python3

import os
import tempfile
import threading

import logging

from util import sanitize
logger = logging.getLogger(__name__)

from sort import SortInfo, sort_titles

from disc import eject_disc
from interface import Interface, PlaintextInterface, Target
from makemkv import rip_disc
from toc import TOC

import features


EPISODE_LENGTH_TOLERANCE = 90

def rip_titles(
    source: str, 
    dest_path: str, 
    toc: TOC,
    sort_info: SortInfo,
    rip_all=False,
    interface: Interface = PlaintextInterface(),
    temp_prefix: str = None,
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
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

  logger.debug(f'rip_content() computed rip_path: {rip_path}')

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print(f"These titles will be copied to {sort_info.base_path()}", target=Target.SORT)
    logger.info(f"These titles will be copied to {sort_info.base_path()}")

    with open(os.path.join(rip_path, sanitize(f'{toc.source.name}-makemkvcon.txt')), 'w') as file:
      file.writelines(toc.lines)
      file.write(toc.source)

    if rip_all:
      rip_disc(source, rip_path, rip_titles=['all'], interface=interface)
    else:
      rip_disc(source, rip_path, rip_titles=sort_info.main_indexes, interface=interface)
      rip_disc(source, rip_path, rip_titles=sort_info.extra_indexes, interface=interface)

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