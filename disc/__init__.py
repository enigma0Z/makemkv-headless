#!/usr/bin/env python3

import os
import shlex
import time

from util import grep, notify

def disc_inserted(source):
  if (source.startswith('dev') or source.startswith('disc')):
    return not grep('please insert', os.popen(shlex.join(['drutil', 'discinfo'])).readlines())

def wait_for_disc_inserted(source, print=print):
  if not disc_inserted(source):
    print(f'Please insert a disc into {source}')
    notify(f'Please insert a disc into {source}')
  while not disc_inserted(source):
    time.sleep(1)

def eject_disc(source, print=print):
  if (source.startswith('disc') or source.startswith('dev')):
    print("Ejecting Disc")
    while(disc_inserted(source)):
      time.sleep(1)
      os.popen(shlex.join([ 'drutil', 'eject' ]))
      os.popen(shlex.join([ 'diskutil', 'eject', source ]))
    else:
      print('Disc already ejected')