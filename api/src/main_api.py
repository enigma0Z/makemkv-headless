import logging
import uvicorn

from argparse import ArgumentParser
from sys import exit, argv
from src.config import CONFIG

CONFIG.update_from_file('./config.yaml')

parser = ArgumentParser()
parser.add_argument("--source")
parser.add_argument("--log-level")
parser.add_argument("--log-file")
parser.add_argument("--port")
parser.add_argument("--frontend")
parser.add_argument("--cors-origin", action='append')
opts = parser.parse_args(argv[1:])

if opts.source is not None:
  CONFIG.source = opts.source

if opts.port is not None:
  CONFIG.listen_port = int(opts.port)

if opts.frontend is not None:
  CONFIG.frontend = opts.frontend

if opts.cors_origin is not None:
  CONFIG.cors_origins = opts.cors_origin

if opts.log_file is not None:
  CONFIG.log_file = opts.log_file

if opts.log_level is not None:
  CONFIG.log_level = opts.log_level

# Erase log file
open(CONFIG.log_file, 'w').close()

logging.basicConfig(
  style='{', 
  format='{asctime} [{levelname}] {filename}:{lineno} {threadName} - {message}', 
  level=CONFIG.get_log_level(),
  filename=CONFIG.log_file,
  filemode='a'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
  from src.api import app
  logger.info(f'Starting app {app}')
  uvicorn.run(app, host="0.0.0.0", port=CONFIG.listen_port) 