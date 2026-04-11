#!/usr/bin/env python3

import os
import tempfile
# import threading

import logging

from makemkv_headless_api import features
from makemkv_headless_api.interface import get_interface
from makemkv_headless_api.interface.target import Target
from makemkv_headless_api.makemkv.asyncio import rip_disc
logger = logging.getLogger(__name__)

from makemkv_headless_api.sort import SortInfo, sort_titles

from makemkv_headless_api.toc import Toc


EPISODE_LENGTH_TOLERANCE = 90

async def rip_titles(
    source: str, 
    dest_path: str, 
    sort_info: SortInfo,
    toc: Toc,
    rip_all=False,
    temp_prefix: str = None,
  ):

  interface = get_interface()
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''
  logger.debug(
    'async rip_titles() called with args; '
    f'source: {source}, '
    f'dest_path: {dest_path}, '
    f'sort_info: {sort_info}, '
    f'rip_all: {rip_all}, '
    f'interface: {interface}, '
    f'temp_prefix: {temp_prefix}'
  )

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  logger.debug(f'Creating temp file at {temp_prefix}')
  rip_path_base = tempfile.mkdtemp(prefix=temp_prefix)
  rip_path = os.path.join(rip_path_base, sort_info.path())

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  logger.debug(f'rip path created at {rip_path}')
  logger.debug(f'rip_content() computed rip_path: {rip_path}')

  if features.DO_RIP:
    interface.print(f"These titles will be copied to {sort_info.base_path()}", target=Target.SORT)

    if rip_all:
      await rip_disc(
        source, rip_path,
        rip_titles=['all'], 
      )

    else:
      await rip_disc(
        source, rip_path,
        rip_titles=sort_info.main_indexes,
      )

      await rip_disc(
        source, rip_path,
        rip_titles=sort_info.extra_indexes,
      )

    await sort_titles(
      toc=toc,
      rip_path_base=rip_path_base,
      dest_path_base=dest_path,
      sort_info=sort_info,
      interface=interface
    )