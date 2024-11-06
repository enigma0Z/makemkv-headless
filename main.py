#!/usr/bin/env python3

import os
import signal
import sys

from argparse import ArgumentParser
from curses_interface import CursesInterface
from movie import rip_movie_interactive
from show import rip_show_interactive

import features

from util import input_with_default

def interactive_rip(
    source, dest_dir,
    source_path: str = None,
    print_input=print,
    print_mkv=print,
    print_sort=print,
    print_status=print,
    get_input=input_with_default,
  ):
  media_choices = ['Blu-Ray', 'DVD']
  media_choices_casefold = [choice.casefold() for choice in media_choices]
  media = None

  content_choices = ['Show', 'Movie']
  content_choices_casefold = [choice.casefold() for choice in content_choices]
  content = None

  rip_args = {}

  while True:
    media = get_input(
      'Is this Blu-Ray or DVD?', 
      media, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in media_choices_casefold]
    )

    print_input('Media:', media)

    content = get_input(
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

    new_dest_dir = os.path.join(dest_dir, media, 'Main', content + 's')
    print_input(new_dest_dir)

    if content.casefold() == 'show':
      rip_args = rip_show_interactive(
        source, 
        new_dest_dir, 
        **rip_args, 
        batch=False, 
        source_path=source_path,
        print_input=print_input,
        print_mkv=print_mkv,
        print_sort=print_sort,
        print_status=print_status,
        get_input=get_input,
      )

    elif content.casefold() == 'movie':
      rip_args = rip_movie_interactive(
        source, 
        new_dest_dir, 
        **rip_args, 
        batch=False,
        print_input=print_input,
        print_mkv=print_mkv,
        print_sort=print_sort,
        print_status=print_status,
        get_input=get_input,
      )

if __name__=='__main__':
  parser = ArgumentParser()
  parser.add_argument('source', default="disc:0")
  parser.add_argument('dest_dir')
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

  opts = parser.parse_args(sys.argv[1:])

  features.DO_SORT = not opts.skip_sort
  features.DO_RIP = not opts.skip_rip
  features.DO_COPY = not opts.skip_copy
  features.DO_CLEANUP = not opts.skip_cleanup
  features.DO_SPLIT = not opts.skip_split

  if not opts.curses:
    def sigint_handler(signal, frame):
      print('Press Ctrl-Z and kill job to cancel')

    signal.signal(signal.SIGINT, sigint_handler)
    os.setpgrp() # Blocks sub-processes from receiving ctrl-c

  if opts.mode is None:
    if opts.curses:
      with CursesInterface() as iface:
        interactive_rip(
          opts.source, 
          opts.dest_dir, 
          source_path=opts.source_path,
          print_input=iface.input_w.print,
          print_mkv=iface.mkv_w.print,
          print_sort=iface.sort_w.print,
          print_status=iface.status_w.print,
          get_input=iface.input_with_default
        )
    else:
      interactive_rip(opts.source, opts.dest_dir, source_path=opts.source_path)
  elif opts.mode.startswith('movie'):
    if opts.batch:
      rip_movie_interactive(opts.source, opts.dest_dir, batch=True)
    else:
      rip_movie_interactive(opts.source, opts.dest_dir, batch=False)
  elif opts.mode.startswith('show'):
    if opts.batch:
      rip_show_interactive(opts.source, opts.dest_dir, batch=True)
    else:
      # TODO: If params provided to rip show immediately do it
      # Need source, dest, episode indexes, extras indexes, show name, season number, first ep, tmdb id
      # Else rip a single disc (i.e. not batch mode) interactively
      rip_show_interactive(opts.source, opts.dest_dir, batch=False)
