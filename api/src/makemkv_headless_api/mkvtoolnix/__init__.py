#!/usr/bin/env python3

import os
import subprocess

import logging

from src.interface.base_interface import BaseInterface
from src.interface.plaintext_interface import PlaintextInterface
from src.interface.target import Target
logger = logging.getLogger(__name__)

MKVMERGE='/opt/homebrew/bin/mkvmerge'

def split_mkv(
    input: str, 
    output: str, 
    chapters: list[int], 
    interface: BaseInterface = PlaintextInterface()
  ):
  with subprocess.Popen(
    [
      MKVMERGE, 
      '--output', output,
      '--split', f'chapters:{','.join([str(v) for v in chapters])}',
      input
    ], 
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=os.setpgrp
  ) as process, open('mkvtoolnix.log', 'w') as log:
    for b_line in process.stdout:
      line = b_line.decode('UTF-8').strip()
      interface.print(line, target=Target.SORT)
      logger.info(line)

    process.wait()

  if (process.returncode > 0):
    interface.print('There was an error splitting the output file, see above', target=Target.SORT)