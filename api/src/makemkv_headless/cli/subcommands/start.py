
from argparse import Namespace
from importlib import resources
import logging
import logging.config
from sys import argv
import uvicorn

from os import fork
from os.path import basename

import yaml

from makemkv_headless.config import CONFIG
from makemkv_headless.cli.parsers import subparsers

from makemkv_headless import config

def main(opts: Namespace):
  CONFIG.load(opts)

  with open(resources.files(config) / 'logging.yaml') as file:
    log_config = yaml.safe_load(file)
    log_config['loggers']['']['level'] = CONFIG.log_level
    if CONFIG.log_file:
      # Erase the log file
      with open(CONFIG.log_file, 'w'):
        pass
      log_config['handlers']['default']['class'] = 'logging.FileHandler'
      log_config['handlers']['default']['filename'] = CONFIG.log_file

  # Erase log file
  if CONFIG.log_file:
    open(CONFIG.log_file, 'w').close()

  logging.config.dictConfig(log_config)
  logger = logging.getLogger(__name__)

  CONFIG.normalize_paths()
  from makemkv_headless.api import app
  logger.info(f'Starting app {app} with config {CONFIG}')
  server_config = uvicorn.Config(
    app=app, 
    host="0.0.0.0", 
    port=CONFIG.listen_port,
    log_config=log_config
  )

  pid = 0

  if (CONFIG.daemon):
    pid = fork()

  if (pid == 0):
    server = uvicorn.Server(server_config)
    server.run()
  else:
    with open(CONFIG.pid_file, 'w') as file:
      print(pid, file=file)

parser = subparsers.add_parser('start', help='Start the makemkv headless server')
parser.set_defaults(func=main)

CONFIG.initialize_parser(parser) # Add CLI-aligned options to parser