#!/usr/bin/env python3

import os
import tempfile
import threading

import logging

from src.rip_titles.threaded import RipTitlesThread
logger = logging.getLogger(__name__)

from src.sort import SortInfo

from src.interface import BaseInterface, PlaintextInterface, Target
from src.toc import TOC


EPISODE_LENGTH_TOLERANCE = 90

def rip_titles(
    source: str, 
    dest_path: str, 
    sort_info: SortInfo,
    toc: TOC = None,
    rip_all=False,
    interface: BaseInterface = PlaintextInterface(),
    temp_prefix: str = None,
  ):
  '''
  `<dir>/<show_name>/Season <season_number>/<show_name> S<season_number>E<episode_number>.mkv`
  '''
  thread = RipTitlesThread(kwargs = {
    "source": source,
    "dest_path": dest_path,
    "sort_info": sort_info,
    "toc": toc,
    "rip_all": rip_all,
    "interface": interface,
    "temp_prefix": temp_prefix
  })
  
  thread.start()
  thread.join()