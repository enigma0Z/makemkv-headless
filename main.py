#!/usr/bin/env python3

import os
import signal
import sys

from argparse import ArgumentParser
from movie import rip_movie_interactive
from show import rip_show_interactive

import features

from util import input_with_default

def interactive_rip(
    source, dest_dir,
    source_path: str = None
  ):
  media_choices = ['Blu-Ray', 'DVD']
  media_choices_casefold = [choice.casefold() for choice in media_choices]
  media = None

  content_choices = ['Show', 'Movie']
  content_choices_casefold = [choice.casefold() for choice in content_choices]
  content = None

  rip_args = {}

  while True:
    media = input_with_default(
      'Is this Blu-Ray or DVD?', 
      media, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in media_choices_casefold]
    )

    print('Media:', media)

    content = input_with_default(
      'Is this a show or movie?', 
      content, 
      lambda v: 
        v.casefold() in [choice.casefold() for choice in content_choices_casefold]
    )

    media = media_choices[media_choices_casefold.index(media.casefold())]
    content = content_choices[content_choices_casefold.index(content.casefold())]

    dest_dir = os.path.join(dest_dir, media, 'Main', content + 's')
    print(dest_dir)

    if content.casefold() == 'show':
      rip_args = rip_show_interactive(source, dest_dir, **rip_args, batch=False, source_path=source_path)

    elif content.casefold() == 'movie':
      rip_args = rip_movie_interactive(source, dest_dir, **rip_args, batch=False)

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

  opts = parser.parse_args(sys.argv[1:])

  features.DO_SORT = not opts.skip_sort
  features.DO_RIP = not opts.skip_rip
  features.DO_COPY = not opts.skip_copy
  features.DO_CLEANUP = not opts.skip_cleanup
  features.DO_SPLIT = not opts.skip_split

  def sigint_handler(signal, frame):
    print('Press Ctrl-Z and kill job to cancel')

  signal.signal(signal.SIGINT, sigint_handler)

  if opts.mode is None:
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
