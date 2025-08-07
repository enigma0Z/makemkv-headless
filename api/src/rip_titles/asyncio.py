#!/usr/bin/env python3

import os
import tempfile
# import threading

import logging

from src import features
from src.interface import get_interface
from src.interface.base_interface import BaseInterface
from src.interface.target import Target
from src.makemkv.asyncio import rip_disc
logger = logging.getLogger(__name__)

from src.sort import SortInfo

from src.toc import TOC


EPISODE_LENGTH_TOLERANCE = 90

async def rip_titles(
    source: str, 
    dest_path: str, 
    sort_info: SortInfo,
    toc: TOC = None,
    rip_all=False,
    interface: BaseInterface = get_interface(),
    temp_prefix: str = None,
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''
  logger.debug(
    'async rip_titles() called with args; '
    f'source: {source}, '
    f'dest_path: {dest_path}, '
    f'toc: <REDACTED>, '
    f'sort_info: {sort_info}, '
    f'rip_all: {rip_all}, '
    f'interface: {interface}, '
    f'temp_prefix: {temp_prefix}'
  )

  # Set rip dir to a temporary file location for extraction to enable more
  # stable rips when the destination is a network location
  rip_path_base = tempfile.mkdtemp(prefix=temp_prefix)
  logger.debug(f'tempfile created at {rip_path_base}')
  rip_path = os.path.join(rip_path_base, sort_info.path())
  logger.debug(f'rip path created at {rip_path}')

  logger.debug(f'rip_content() computed rip_path: {rip_path}')

  os.makedirs(os.path.join(
    rip_path,
    'extras'
  ), exist_ok=True)

  if features.DO_RIP:
    interface.print(f"These titles will be copied to {sort_info.base_path()}", target=Target.SORT)

    # if (toc != None):
    #   with open(os.path.join(rip_path, sanitize(f'{toc.source.name}-makemkvcon.txt')), 'w') as file:
    #     file.writelines(toc.lines)
    #     file.write(f'{toc.source}')

    if rip_all:
      await rip_disc(
        source, rip_path,
        rip_titles=['all'], 
        interface=interface
      )

    else:
      await rip_disc(
        source, rip_path,
        rip_titles=sort_info.main_indexes,
        interface=interface
      )

      await rip_disc(
        source, rip_path,
        rip_titles=sort_info.extra_indexes,
        interface=interface
      )

      # threading.Thread(
      #   kwargs={
      #     'toc': toc,
      #     'rip_path_base': rip_path_base,
      #     'dest_path_base': dest_path,
      #     'sort_info': sort_info,
      #     'interface': interface
      #   },
      #   target=sort_titles,
      #   daemon=True
      # ).start()