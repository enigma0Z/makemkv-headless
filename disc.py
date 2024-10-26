#!/usr/bin/env python3

import os
import shlex
import subprocess

from util import grep, notify

MAKEMKVCON="/Applications/MakeMKV.app/Contents/MacOS/makemkvcon"

def disc_inserted(source):
  if (source.startswith('dev')):
    device = source.split(':')[1]
    return not grep('could not find disk', os.popen(shlex.join(['diskutil', 'info', device]) + " 2>&1").readlines())
  elif (source.startswith('disc')):
    print("WARNING: makemkvcon index and drutil index do not always line up, this mode is buggy and should be avoided")
    drutil_index = int(source.split(':')[1]) + 1
    return not grep('please insert', os.popen(shlex.join(['drutil', '-drive', str(drutil_index), 'discinfo'])).readlines())

def wait_for_disc_inserted(source):
  if not disc_inserted(source):
    print(f'Please insert a disc into {source}')
    notify(f'Please insert a disc into {source}')
  while not disc_inserted(source):
    time.sleep(1)

def eject_disc(source):
  if (source.startswith('dev')):
    device = source.split(':')[1]
    return os.popen(shlex.join(['diskutil', 'eject', device]))
  elif (source.startswith('disc')):
    print("WARNING: makemkvcon index and drutil index do not always line up, this mode is buggy and should be avoided")
    drutil_index = int(source.split(':')[1]) + 1
    os.system(shlex.join([ 'drutil', '-drive', str(drutil_index), 'eject' ]))

def rip_disc(
    source, 
    dest,
    rip_titles=['all']
  ):
  notify(f'Backing up {source} to {dest}')
  print(f'Backing up {source} to {dest}')

  wait_for_disc_inserted(source)

  # Do the actual rip + eject the disc when done
  for rip_title in [str(v) for v in rip_titles]:
    print(f'Ripping title {rip_title}')
    notify(f'Ripping title {rip_title}')
    # os.system(shlex.join([ MAKEMKVCON, 'mkv', source, rip_title, dest]))
    subprocess.Popen([ MAKEMKVCON, 'mkv', source, rip_title, dest]).wait()