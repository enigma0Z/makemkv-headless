#!/usr/bin/env python3

import os
import subprocess

MKVMERGE='/opt/homebrew/bin/mkvmerge'

def split_mkv(input: str, output: str, chapters: list[int], print=lambda x: None):
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
  ) as process:
    for b_line in process.stdout:
      line = b_line.decode('UTF-8').strip()
      print(line)

    process.wait()

  if (process.returncode > 0):
    print('There was an error splitting the output file, see above')