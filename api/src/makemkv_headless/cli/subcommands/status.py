
from argparse import Namespace
from signal import SIGTERM
from sys import argv

from os import SEEK_CUR, SEEK_END, kill, unlink
from os.path import basename, exists

from makemkv_headless.cli.parsers import subparsers
from makemkv_headless.config import CONFIG

def main(opts: Namespace):
  CONFIG.load(opts)

  try:
    with open(CONFIG.pid_file, 'r') as pid_file:
      pid = int(pid_file.readline())
    kill(pid, 0)
    print('Status: Running')
    if opts.tail_log is not None and exists(CONFIG.log_file):
      with open(CONFIG.log_file, 'rb') as log_file:
        num_lines = 10
        log_file.seek(-2, SEEK_END)
        try:
          while (num_lines > 0):
            if (log_file.read(1) == b'\n'):
              num_lines -= 1

            log_file.seek(-2, SEEK_CUR)
        except OSError:
          pass
          
        log_file.seek(2, SEEK_CUR)
        tail_lines = ''.join([line.decode() for line in log_file.readlines()])
        print('---')
        print(tail_lines)
  except ProcessLookupError:
    print(f'Status: Stopped')
  except FileNotFoundError:
    print(f'Could not locate pid file {CONFIG.pid_file}')

parser = subparsers.add_parser('status', help='Display status of the configured makemkv headless')
parser.set_defaults(func=main)

CONFIG.initialize_parser(parser, ['config_file', 'pid_file'])
parser.add_argument(
  '--tail-log', '-t', 
  nargs=1,
  metavar='TAIL_LINES',
  help='Print this many log lines from the configured log file'
)