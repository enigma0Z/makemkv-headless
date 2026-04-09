#!/usr/bin/env python3

import os
import shlex
import time

from sys import platform

from src.config import CONFIG
from src.interface import get_interface
from src.interface.plaintext_interface import PlaintextInterface
from src.interface.target import Target
from src.util import cmd, grep, notify

def disc_inserted(source):
  if source.startswith('dev'):
    match platform:
      case 'darwin':
        return not grep('please insert', os.popen(shlex.join(['drutil', 'discinfo'])).readlines())
      case 'linux':
        # TODO: Figure out error status here
        return os.popen(shlex.join(['eject', '--noop', source.split(':')[1]]))
  else:
    return True

def wait_for_disc_inserted(
    source, 
    interface=get_interface()
  ):
  if not disc_inserted(source):
    interface.print(f'Please insert a disc into {source}', target=Target.INPUT)
    notify(f'Please insert a disc into {source}')
  while not disc_inserted(source):
    time.sleep(1)

async def eject_disc(
    source, 
    interface=get_interface()
  ):
  if (source.startswith('disc') or source.startswith('dev')):
    interface.print("Ejecting Disc", target=Target.INPUT)
    match platform:
        case 'darwin':
          await cmd('drutil', 'eject')
          await cmd('diskutil', 'eject')
        case 'linux':
          await cmd('eject', CONFIG.source.split(':')[1])