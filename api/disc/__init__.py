#!/usr/bin/env python3

import os
import shlex
import time

from ..interface import PlaintextInterface
from ..util import grep, notify

def disc_inserted(source):
  if (source.startswith('dev') or source.startswith('disc')):
    return not grep('please insert', os.popen(shlex.join(['drutil', 'discinfo'])).readlines())

def wait_for_disc_inserted(
    source, 
    interface=PlaintextInterface()
  ):
  if not disc_inserted(source):
    interface.print(f'Please insert a disc into {source}', target='input')
    notify(f'Please insert a disc into {source}')
  while not disc_inserted(source):
    time.sleep(1)

def eject_disc(
    source, 
    interface=PlaintextInterface()
  ):
  if (source.startswith('disc') or source.startswith('dev')):
    interface.print("Ejecting Disc", target='input')
    while(disc_inserted(source)):
      time.sleep(1)
      os.popen(shlex.join([ 'drutil', 'eject' ]))
      os.popen(shlex.join([ 'diskutil', 'eject', source ]))