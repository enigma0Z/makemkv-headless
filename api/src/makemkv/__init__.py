#!/usr/bin/env python3

import re
import subprocess
from time import time

import logging
logger = logging.getLogger(__name__)

from config import CONFIG
from disc import wait_for_disc_inserted
from interface import BaseInterface, PlaintextInterface, Target
from util import notify, seconds_to_hms

import disc
import util

def rip_disc(
    source, 
    dest,
    rip_titles=['all'],
    interface: BaseInterface = PlaintextInterface(),
  ):
  logger.info(f'Backing up {source} to {dest}')
  interface.print(f'Backing up {source} to {dest}', target=Target.SORT)

  wait_for_disc_inserted(source, interface)

  # Do the actual rip + eject the disc when done
  for rip_title in [str(v) for v in rip_titles]:
    logger.info(f'Ripping title {rip_title}')
    interface.print(f'Ripping title {rip_title}', target=Target.SORT)

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
      [ CONFIG.makemkvcon_path, '--noscan', '--robot', '--progress=-same', 'mkv', source, rip_title, dest],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
    ) as process, open('makemkv.log', 'w') as log:
      current_title=None
      current_start = None
      current_elapsed = 0
      current_remaining = 0

      total_title=None
      total_elapsed = 0
      total_remaining = 0
      total_start = None

      progress_value=None

      for b_line in process.stdout:
        line = b_line.decode().strip()
        logger.debug(f'makemkvcon - {line}')

        if line.startswith('PRGC'):
          current_title = line.split(':')[1].split(',')[2]
          current_title = re.sub(r'^"', '', current_title)
          current_title = re.sub(r'"$', '', current_title)
        elif line.startswith('PRGT'):
          total_title = line.split(':')[1].split(',')[2]
          total_title = re.sub(r'^"', '', total_title)
          total_title = re.sub(r'"$', '', total_title)
        elif line.startswith('PRGV'):
          progress_value = [int(v) for v in line.split(':')[1].split(',')]

        else:
          try:
            if (line.startswith('MSG')):
                match = re.match(r'.+?:\d+?,\d+?,\d+?,"(.+?)(?<!\\)",', line)
                msg_line = match.group(1)

                interface.print(msg_line, target=Target.MKV)
                logger.info(msg_line)
            else:
              interface.print('>', line, target=Target.MKV)
          except Exception as ex:
            interface.print(ex, target=Target.MKV)
            interface.print(line, target=Target.MKV)
            logger.error('Could not format line', ex)

        if None not in [current_title, total_title, progress_value]:
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
            f'{total_pct*100:>6.2f}% {seconds_to_hms(total_elapsed)}s (~{seconds_to_hms(total_remaining)}s) - {total_title}'
          
          current_line = \
            f'{current_pct*100:>6.2f}% {seconds_to_hms(current_elapsed)}s (~{seconds_to_hms(current_remaining)}s) - {current_title}'

          status_line = f'{total_title}, {current_title} - {total_pct*100:>6.2f}% ~{seconds_to_hms(total_remaining)}s / {current_pct*100:>6.2f}% ~{seconds_to_hms(current_remaining)}s'

          # interface.send(ProgressMessage(
          #   total=total_pct,
          #   total_elapsed=total_elapsed,
          #   total_remaining=total_remaining,
          #   current=current_pct,
          #   current_elapsed=current_elapsed,
          #   current_remaining=current_remaining
          # ))

          interface.print(total_line, current_line, sep='\n', target=Target.STATUS)
          interface.title(status_line, target=Target.MKV)