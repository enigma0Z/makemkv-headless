import logging
import uvicorn

from argparse import ArgumentParser
from sys import exit, argv
from makemkv_headless_api.config import CONFIG
from makemkv_headless_api.models.config import ConfigModel

def main():
  # parser = ArgumentParser()

  # for (_, value) in ConfigModel.model_fields.items():
  #   args = value.json_schema_extra['cli_argument']['args']
  #   kwargs = value.json_schema_extra['cli_argument']['kwargs']
  #   parser.add_argument(*args, **kwargs)

  # opts = parser.parse_args(argv[1:])

  # # Load config file into opts
  # if ('config_file' in opts and opts.config_file is not None):
  #   CONFIG.config_file = opts.config_file

  # CONFIG.update_from_file(CONFIG.config_file)

  # print(opts)

  # for key in ConfigModel.model_fields:
  #   try:
  #     opt = getattr(opts, key)
  #   except AttributeError:
  #     print(f"Could not retrieve option for config {key}")
  #     continue

  #   if opt is not None:
  #     print(f'setting config {key} to {opt}')
  #     setattr(CONFIG, key, opt)
  #   else:
  #     print(f'Leaving config {key} at value {getattr(CONFIG, key)}')

  CONFIG.load()

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
  from makemkv_headless_api.api import app
  logger.info(f'Starting app {app} with config {CONFIG}')
  uvicorn.run(app, host="0.0.0.0", port=CONFIG.listen_port) 