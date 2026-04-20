from argparse import ArgumentParser
import logging
from sys import argv
import uvicorn

from os import fork

from makemkv_headless.config import CONFIG

def main():
  parser = ArgumentParser()
  CONFIG.initialize_parser(parser)

  opts = parser.parse_args(argv[1:])
  CONFIG.load(opts)

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

  CONFIG.normalize_paths()
  from makemkv_headless.api import app
  logger.info(f'Starting app {app} with config {CONFIG}')
  config = uvicorn.Config(app=app, host="0.0.0.0", port=CONFIG.listen_port)
  server = uvicorn.Server(config)
  server.run()

if __name__ == '__main__':
  main()