#!/usr/bin/env python3

import os
import tempfile
import threading

import logging
from typing import TypedDict

from src.interface import get_interface
from src.interface.base_interface import BaseInterface
from src.interface.target import Target
from src.makemkv.threaded import RipDiscThread
from src.threads import StoppableThread
from src.util import sanitize
logger = logging.getLogger(__name__)

from src.sort import SortInfo, sort_titles

from src.disc import eject_disc
from src.makemkv import rip_disc
from src.toc import Toc

from src import features

EPISODE_LENGTH_TOLERANCE = 90

class RipTitlesArgs(TypedDict):
  source: str
  dest_path: str
  sort_info: SortInfo
  toc: Toc
  rip_all: bool
  interface: BaseInterface
  temp_prefix: str

class RipTitlesThread(StoppableThread):
  def __init__(self, kwargs: RipTitlesArgs, *_args, **_kwargs):
    super().__init__(kwargs=kwargs, *_args, *_kwargs)

  def __call__(
      self,
      source: str, 
      dest_path: str, 
      sort_info: SortInfo,
      toc: Toc = None,
      rip_all=False,
      interface: BaseInterface = get_interface(),
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

      if (toc != None):
        with open(os.path.join(rip_path, sanitize(f'{toc.source.name}-makemkvcon.txt')), 'w') as file:
          file.writelines(toc.lines)
          file.write(f'{toc.source}')

      rip_disc_threads: list[threading.Thread] = []

      if rip_all:
        rip_disc_threads.append(RipDiscThread(
          args=[source, rip_path], 
          kwargs={
            "rip_titles": ['all'], 
            "interface": interface
          }
        ))
      else:
        rip_disc_threads.append(RipDiscThread(
          args=[source, rip_path],
          kwargs={
            "rip_titles": sort_info.main_indexes,
            "interface": interface
          }
        ))
        rip_disc_threads.append(RipDiscThread(
          args=[source, rip_path],
          kwargs={
            "rip_titles": sort_info.extra_indexes,
            "interface": interface
          }
        ))

      for thread in rip_disc_threads:
        thread.start()
        while thread.is_alive():
          self._stop_event.wait(timeout=1)
          if (self.stop_requested()):
            logger.debug(f'Thread {thread} stop requested')
            thread.stop()
            thread.join()
            break
          
        if (self.stop_requested()):
          break

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
