#!/usr/bin/env python3

import os
import signal
import sys

import logging

from src.interactive import interactive_rip
from src.rip_titles.interactive import rip_movie_interactive, rip_show_interactive

from argparse import ArgumentParser

from src import features

from src.config import CONFIG
from src.interface.curses_interface import CursesInterface
# from src.api.singletons.singletons import start_api

logger = logging.getLogger(__name__)

def parse_args():
  parser = ArgumentParser()
  parser.add_argument('-s', '--source')
  parser.add_argument('-d', '--destination')
  parser.add_argument('--config-file', default="./config.yaml")
  parser.add_argument('--mode', action='store')
  parser.add_argument('--batch', action='store_true')
  parser.add_argument('--imdbid', action='store', default=None)
  parser.add_argument('--tmdbid', action='store', default=None)
  parser.add_argument('--skip-sort', action='store_true')
  parser.add_argument('--skip-rip', action='store_true')
  parser.add_argument('--skip-copy', action='store_true')
  parser.add_argument('--skip-cleanup', action='store_true')
  parser.add_argument('--skip-split', action='store_true')
  parser.add_argument('--curses', action='store_true')
  parser.add_argument('--temp-prefix', action='store', default=None)
  parser.add_argument('--api', action='store_true')
  parser.add_argument('--log-level', action='store', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])
  parser.add_argument('--log-file', default=None)

  opts = parser.parse_args(sys.argv[1:])

  CONFIG.update_from_file(opts.config_file)

  if opts.log_level:
    CONFIG.update(log_level = opts.log_level)

  match CONFIG.log_level:
    case 'ERROR':
      log_level = logging.ERROR
    case 'WARNING': 
      log_level = logging.WARNING
    case 'INFO': 
      log_level = logging.INFO
    case 'DEBUG': 
      log_level = logging.DEBUG
    case _:
      log_level = logging.INFO

  logging.basicConfig(
    filename=opts.log_file, 
    style='{', 
    format='{asctime} [{levelname}] {filename}:{lineno} {threadName} - {message}', 
    level=log_level
  )

  if opts.source:
    CONFIG.update(source=opts.source)

  if opts.destination:
    CONFIG.update(destination=opts.destination)

  if opts.temp_prefix:
    CONFIG.update(temp_prefix=opts.temp_prefix)

  logging.info('Starting makemkv-headless')

  features.DO_SORT = not opts.skip_sort
  features.DO_RIP = not opts.skip_rip
  features.DO_COPY = not opts.skip_copy
  features.DO_CLEANUP = not opts.skip_cleanup
  features.DO_SPLIT = not opts.skip_split
  
  return opts

def main_cli(): 
  opts = parse_args()

  try:
    if (opts.api): 
      # start_api()
      sys.exit(0)

    elif not opts.curses:
      def sigint_handler(signal, frame):
        print('Press Ctrl-Z and kill job to cancel')

      signal.signal(signal.SIGINT, sigint_handler)
      os.setpgrp() # Blocks sub-processes from receiving ctrl-c

    interface = PlaintextInterface()
    if opts.curses:
      interface = CursesInterface()

    if opts.mode is None:
      with interface:
        interactive_rip(
          opts.source, 
          opts.destination, 
          interface=interface,
          temp_prefix=opts.temp_prefix
        )
    elif opts.mode.startswith('movie'):
      if opts.batch:
        rip_movie_interactive(opts.source, opts.destination, batch=True, temp_prefix=opts.temp_prefix)
      else:
        rip_movie_interactive(opts.source, opts.destination, batch=False, temp_prefix=opts.temp_prefix)
    elif opts.mode.startswith('show'):
      if opts.batch:
        rip_show_interactive(opts.source, opts.destination, batch=True, temp_prefix=opts.temp_prefix)
      else:
        # TODO: If params provided to rip show immediately do it
        # Need source, dest, episode indexes, extras indexes, show name, season number, first ep, tmdb id
        # Else rip a single disc (i.e. not batch mode) interactively
        rip_show_interactive(opts.source, opts.destination, batch=False, temp_prefix=opts.temp_prefix)
  except Exception as ex:
    logger.error(ex)
    raise ex
