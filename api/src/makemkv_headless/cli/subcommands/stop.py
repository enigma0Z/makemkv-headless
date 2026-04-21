
from argparse import Namespace
from signal import SIGTERM
from sys import argv

from os import kill, unlink
from os.path import basename, exists

from makemkv_headless.cli.parsers import subparsers
from makemkv_headless.config import CONFIG
from makemkv_headless.models.config import ConfigModel

def main(opts: Namespace):
  CONFIG.load(opts)

  try:
    with open(CONFIG.pid_file, 'r') as file:
      pid = int(file.readline())
      print('Stopping pid', pid)
      kill(pid, SIGTERM)
  except ProcessLookupError:
    print(f'No {basename(argv[0])} server running')
  except FileNotFoundError:
    print(f'Could not locate pid file {CONFIG.pid_file}')

  if exists(CONFIG.pid_file):
    unlink(CONFIG.pid_file)

parser = subparsers.add_parser('stop', help='Stop the makemkv headless server running from the given pidfile')
parser.set_defaults(func=main)

CONFIG.initialize_parser(parser, ['config_file', 'pid_file'])