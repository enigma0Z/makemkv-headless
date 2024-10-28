#!/usr/bin/env python3

from math import trunc
import os
import re
import shlex
import subprocess

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
  os.popen(shlex.join([
    'osascript', '-e',
    f'display notification "{message}" with title "Disc Backup"'
  ]))

def rsync(source, dest):
  # Put output files into their final destinations if the rip was done locally
  print(f'Copying local rip from {source} to {dest}')
  notify(f'Copying local rip to {dest}')
  subprocess.Popen([
    'rsync', '-av',
    f'{source}', dest
  ]).wait()

def sanitize(value: str): # Strips out non alphanumeric characters and replaces with "_"
  return re.sub(r'[^\w]', '_', value.lower())

def string_to_list_int(_input):
  if (type(_input) is list):
    return _input

  elif (type(_input) is None):
    return []

  new_list = [
    v 
    for v 
    in re.sub(r'[^,\d-]', '', _input).split(',')
    if v != ''
  ]

  for index, value in enumerate(new_list):
    if type(value) is int:
      pass

    elif '-' in value:
      start, end = [int(v) for v in value.split('-')]
      new_list.remove(value)
      for inner_index, value in enumerate(range(start, end + 1)):
        new_list.insert(index + inner_index, int(value))
    
    else:
      new_list[index] = int(value)

  return new_list

def input_with_default(
    prompt, 
    value=None,
    validation = lambda v: v != '' and v is not None
  ):
  while True:
    _input = input(f'{prompt}\n({value})> ')
    if validation(_input):
      return _input
    elif validation(value):
      return value