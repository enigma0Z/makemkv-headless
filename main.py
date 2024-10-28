#!/usr/bin/env python3

import os
import signal
import sys
import threading
import subprocess
import tempfile

from argparse import ArgumentParser
from time import sleep
from movie import rip_movie_interactive
from show import rip_show_interactive

from features import *

if __name__=='__main__':
  parser = ArgumentParser()
  parser.add_argument('source', default="disc:0")
  parser.add_argument('dest_dir')
  parser.add_argument('--mode', action='store', default='movies')
  parser.add_argument('--batch', action='store_true')
  parser.add_argument('--imdbid', action='store', default=None)
  parser.add_argument('--tmdbid', action='store', default=None)
  parser.add_argument('--skip-sort', action='store_true')
  parser.add_argument('--skip-rip', action='store_true')
  parser.add_argument('--skip-copy', action='store_true')
  parser.add_argument('--skip-cleanup', action='store_true')
  parser.add_argument('--skip-split', action='store_true')

  opts = parser.parse_args(sys.argv[1:])

  features.DO_SORT = not opts.skip_sort
  features.DO_RIP = not opts.skip_rip
  features.DO_COPY = not opts.skip_copy
  features.DO_CLEANUP = not opts.skip_cleanup
  features.DO_SPLIT = not opts.skip_split
  def sigint_handler(signal, frame):
    print('Press Ctrl-Z and kill job to cancel')

  signal.signal(signal.SIGINT, sigint_handler)
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
