#!/usr/bin/env python3

import re
import shutil
import subprocess
from time import time

from disc import wait_for_disc_inserted
from util import notify, seconds_to_hms

MAKEMKVCON="/Applications/MakeMKV.app/Contents/MacOS/makemkvcon"

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

    # Current and total progress title
    # PRGC:code,id,name (Current)
    # PRGT:code,id,name (Total)
    # code - unique message code
    # id - operation sub-id
    # name - name string
    #
    # Progress bar values for current and total progress
    # PRGV:current,total,max
    # current - current progress value
    # total - total progress value
    # max - maximum possible value for a progress bar, constant 

    with subprocess.Popen(
      [ MAKEMKVCON, '--robot', '--progress=-same', 'mkv', source, rip_title, dest],
      stdout=subprocess.PIPE
    ) as process:
      width = shutil.get_terminal_size().columns

      current_title=None
      current_start = None
      current_elapsed = 0
      current_remaining = 0

      total_title=None
      total_elapsed = 0
      total_remaining = 0
      total_start = None

      progress_value=None

      print('\n'*2, end=None)
      for b_line in process.stdout:
        line = b_line.decode().strip()

        if line.startswith('PRGC'):
          current_title = line.split(':')[1].split(',')[2]
        elif line.startswith('PRGT'):
          total_title = line.split(':')[1].split(',')[2]
        elif line.startswith('PRGV'):
          progress_value = [int(v) for v in line.split(':')[1].split(',')]

        elif (
          not line.startswith('PRGV') 
        ):
          print('\033[F'*4, end=None)
          if (line.startswith('MSG')):
            try:
              match = re.match(r'.+?:\d+?,\d+?,\d+?,"(.+?)(?<!\\)",', line)
              print(match.group(1) + ' ' * (width - len(match.group(1))))
            except:
              print(line)
          
          else:
            print(line)

          print(' '*width + '\n'*2, end=None)

        if None not in [current_title, total_title, progress_value]:
          print('\033[F'*3, end=None)

          total_pct = progress_value[1]/progress_value[2]
          if total_pct == 0:
            total_start = time()
            total_elapsed = 0
          else:
            total_elapsed = time() - total_start
            total_remaining = total_elapsed / total_pct - total_elapsed

          current_pct = progress_value[0]/progress_value[2]
          if current_pct == 0:
            current_start = time()
            current_elapsed = 0
          else:
            current_elapsed = time() - current_start
            current_remaining = current_elapsed / current_pct - current_elapsed

          total_line = \
            f'Total   {total_pct*100:>6.2f}% {seconds_to_hms(total_elapsed)}s (~{seconds_to_hms(total_remaining)}s) - {total_title}'

          current_line = \
            f'Current {current_pct*100:>6.2f}% {seconds_to_hms(current_elapsed)}s (~{seconds_to_hms(current_remaining)}s) - {current_title}'

          total_line += ' ' * (width - len(total_line))
          current_line += ' ' * (width - len(current_line))

          print(total_line)
          print(current_line)