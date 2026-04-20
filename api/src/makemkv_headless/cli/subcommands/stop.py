
from argparse import Namespace
from signal import SIGTERM
from sys import argv

from os import kill, unlink
from os.path import basename, exists

from makemkv_headless.cli.parsers import subparsers

def main(opts: Namespace):
  try:
    with open(opts.pid_file, 'r') as file:
      pid = int(file.readline())
      print('Stopping pid', pid)
      kill(pid, SIGTERM)
  except ProcessLookupError:
    print(f'No {basename(argv[0])} server running')
  except FileNotFoundError:
    print(f'Could not locate pid file {opts.pid_file}')

  if exists(opts.pid_file):
    unlink(opts.pid_file)

parser = subparsers.add_parser('stop', help='Stop the makemkv headless server running from the given pidfile')
parser.set_defaults(func=main)
parser.add_argument(
  '--pid-file', 
  help='The PID file to locate the daemon pid from',
  default=f'{basename(argv[0])}.pid'
)