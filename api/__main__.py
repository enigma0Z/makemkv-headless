#!/usr/bin/env python3

import os
import signal
import sys

import logging
logger = logging.getLogger(__name__)

from argparse import ArgumentParser
from curses_interface import CursesInterface
from interface import Interface, Message, PlaintextInterface, Target
from movie import rip_movie_interactive
from show import rip_show_interactive

import features

from rest_interface.rest_api import app

def interactive_rip(
    source, dest_dir,
    source_path: str = None,
    interface: Interface = PlaintextInterface(),
    **kwargs
  ):
  library_choices = ['kids', 'main']
  library_choices_casefold = [choice.casefold() for choice in library_choices]
  library = 'main'

  media_choices = ['blu-ray', 'dvd']
  media_choices_casefold = [choice.casefold() for choice in media_choices]
  media = None

  content_choices = ['show', 'movie']
  content_choices_casefold = [choice.casefold() for choice in content_choices]
  content = None

  rip_args = {}

  while True:
    library = interface.get_input(
      'Should this go into the Main or Kids library?', 
      library, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in library_choices_casefold]
    )

    media = interface.get_input(
      'Is this Blu-Ray or DVD?', 
      media, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in media_choices_casefold]
    )

    interface.print(f'Media: {media}', target=Target.INPUT)

    content = interface.get_input(
      'Is this a show or movie?', 
      content, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in content_choices_casefold]
    )

    media = media_choices[media_choices_casefold.index(media.casefold())]
    old_content = content
    content = content_choices[content_choices_casefold.index(content.casefold())]
    if (content != old_content):
      rip_args = {}

    new_dest_dir = os.path.join(dest_dir, library, content + 's', media)
    interface.print(new_dest_dir, target=Target.INPUT)

    if content.casefold() == 'show':
      rip_args = rip_show_interactive(
        source, 
        new_dest_dir, 
        **kwargs,
        **rip_args, 
        batch=False, 
        source_path=source_path,
        interface=interface
      )

    elif content.casefold() == 'movie':
      rip_args = rip_movie_interactive(
        source, 
        new_dest_dir, 
        **kwargs,
        **rip_args, 
        batch=False,
        interface=interface
      )

if __name__=='__main__':
  parser = ArgumentParser()
  parser.add_argument('--source', default="disc:0")
  parser.add_argument('--dest-dir')
  parser.add_argument('--mode', action='store')
  parser.add_argument('--batch', action='store_true')
  parser.add_argument('--imdbid', action='store', default=None)
  parser.add_argument('--tmdbid', action='store', default=None)
  parser.add_argument('--skip-sort', action='store_true')
  parser.add_argument('--skip-rip', action='store_true')
  parser.add_argument('--skip-copy', action='store_true')
  parser.add_argument('--skip-cleanup', action='store_true')
  parser.add_argument('--skip-split', action='store_true')
  parser.add_argument('--source-path', action='store')
  parser.add_argument('--curses', action='store_true')
  parser.add_argument('--temp-prefix', action='store', default=None)
  parser.add_argument('--api', action='store_true')
  parser.add_argument('--log-level', action='store', default='INFO', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])

  opts = parser.parse_args(sys.argv[1:])

  if opts.log_level == 'ERROR': 
    log_level = logging.ERROR
  elif opts.log_level == 'WARNING': 
    log_level = logging.WARNING
  elif opts.log_level == 'INFO': 
    log_level = logging.INFO
  elif opts.log_level == 'DEBUG': 
    log_level = logging.DEBUG

  logging.basicConfig(
    filename='app.log', 
    style='{', 
    format='{asctime} [{levelname}] {filename}:{lineno} {threadName} - {message}', 
    level=log_level
  )

  features.DO_SORT = not opts.skip_sort
  features.DO_RIP = not opts.skip_rip
  features.DO_COPY = not opts.skip_copy
  features.DO_CLEANUP = not opts.skip_cleanup
  features.DO_SPLIT = not opts.skip_split

  try:
    if (opts.api): 
      app.run()
      exit(0)

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
          opts.dest_dir, 
          source_path=opts.source_path,
          interface=interface,
          temp_prefix=opts.temp_prefix
        )
    elif opts.mode.startswith('movie'):
      if opts.batch:
        rip_movie_interactive(opts.source, opts.dest_dir, batch=True, temp_prefix=opts.temp_prefix)
      else:
        rip_movie_interactive(opts.source, opts.dest_dir, batch=False, temp_prefix=opts.temp_prefix)
    elif opts.mode.startswith('show'):
      if opts.batch:
        rip_show_interactive(opts.source, opts.dest_dir, batch=True, temp_prefix=opts.temp_prefix)
      else:
        # TODO: If params provided to rip show immediately do it
        # Need source, dest, episode indexes, extras indexes, show name, season number, first ep, tmdb id
        # Else rip a single disc (i.e. not batch mode) interactively
        rip_show_interactive(opts.source, opts.dest_dir, batch=False, temp_prefix=opts.temp_prefix)
  except Exception as ex:
    logger.error(ex)
    raise ex