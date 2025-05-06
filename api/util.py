#!/usr/bin/env python3

from math import trunc
import os
import re
import shutil
import subprocess

import logging
logger = logging.getLogger(__name__)

from interface import PlaintextInterface, Target

def grep(term, lines):
  return True in [ term.casefold() in line.casefold() for line in lines ]

def hms_to_seconds(time):
  [hours, minutes, seconds] = [int(v) for v in time.split(':')]
  hours *= 60 * 60
  minutes *= 60
  return hours + minutes + seconds

def seconds_to_hms(seconds):
  seconds = round(seconds)
  hours = trunc(seconds/60/60)
  minutes = trunc(seconds/60) - hours * 60
  seconds = seconds - hours * 60 * 60 - minutes * 60
  return f'{hours}:{minutes:02d}:{seconds:02d}'

def notify(message):
  subprocess.Popen(
    [
      'osascript', '-e',
      f'display notification "{message}" with title "Disc Backup"'
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  )

def clearing_line(line=' '):
  if len(line) == 0: line = ' '
  return line + ' ' * (-len(line) % shutil.get_terminal_size().columns)

def rsync(source, dest, interface=PlaintextInterface()):
  # Put output files into their final destinations if the rip was done locally
  interface.print(f'Copying local rip from {source} to {dest}', target=Target.SORT)
  notify(f'Copying local rip to {dest}')
  process = subprocess.Popen(
    [ 'rsync', '-av', f'{source}', dest ], 
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=os.setpgrp,
  )

  for b_line in process.stdout:
    line = b_line.decode('utf-8').strip()
    
    interface.print(line, target=Target.SORT)
    logger.info(line)
  
  stderr_lines = []

  for b_line in process.stderr:
    line = b_line.decode('utf-8').strip()
    logger.error(line)
    stderr_lines.append(line)

  if process.returncode == 0:
    line = f'rsync completed successfully for {os.path.split(source)[-1]}'
    interface.print(line, target=Target.SORT)
  else:
    line = f'RSYNC FAILED FOR {dest} with return code {process.returncode}'
    interface.print(line, target=Target.SORT)

    for line in stderr_lines:
      line.strip()
      interface.print(line, target=Target.SORT)

def sanitize(value: str): # Strips out non alphanumeric characters and replaces with "_"
  return re.sub(r'[^\w]', '_', value.lower())

def string_to_list_int(_input):
  if (type(_input) is list):
    return _input

  elif (type(_input) is None):
    return []

  token_list = [
    v 
    for v 
    in re.sub(r'[^,\d-]', '', _input).split(',')
    if v != ''
  ]

  output_list = []

  for index, value in enumerate(token_list):
    if type(value) is int:
      pass

    elif '-' in value:
      start, end = [int(v) for v in value.split('-')]
      new_list = []

      if start <= end:
        for value in range(start, end + 1):
          new_list.append(int(value))
      else:
        for value in reversed(range(end, start + 1)):
          new_list.append(int(value))

      output_list.extend(new_list)
    
    else:
      output_list.append(int(value))

  return output_list


def input_with_default(
    prompt, 
    value=None,
    validation = lambda v: v != '' and v is not None
  ):
  while True:
    _input = input(f'{prompt}\n({value})> ')
    try:
      if _input == '' and value is not None:
        return value
      elif _input.casefold() == 'none':
        return ''
      elif validation(_input):
        return _input
      elif validation(value):
        return value
    except AttributeError:
      print("Error validating input")
      continue