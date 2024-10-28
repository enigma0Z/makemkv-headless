#!/usr/bin/env python3

import os
import shlex

MKVMERGE='/opt/homebrew/bin/mkvmerge'

def split_mkv(input: str, output: str, chapters: list[int]):
  os.system(shlex.join([
    MKVMERGE, 
    '--output', output,
    '--split', f'chapters:{','.join([str(v) for v in chapters])}',
    input
  ]))