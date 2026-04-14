from argparse import ArgumentParser
import json
import logging
from pydantic import ConfigDict
import yaml
from sys import argv

from os.path import abspath

from makemkv_headless_api.models.config import ConfigModel, LogLevelStr

class Config(ConfigModel):
  keys: list[str] = []
  _parser: ArgumentParser

  def __str__(self):
    return f'{super().model_dump(mode='json')}'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._parser = ArgumentParser()

    for (_, value) in ConfigModel.model_fields.items():
      args = value.json_schema_extra['cli_argument']['args']
      kwargs = value.json_schema_extra['cli_argument']['kwargs']
      self._parser.add_argument(*args, **kwargs)

  def load(self):

    opts = self._parser.parse_args(argv[1:])

    # Load config file into opts
    if ('config_file' in opts and opts.config_file is not None):
      self.config_file = opts.config_file

    self.update_from_file(self.config_file)

    for key in self.__class__.model_fields:
      try:
        opt = getattr(opts, key)
      except AttributeError:
        continue

      if opt is not None:
        setattr(CONFIG, key, opt)

  def overwrite(
      self, **kwargs
  ):
    '''Initialize all config values specified, set unspecified values to None'''
    for key in Config.keys:
      self.__dict__[key] = kwargs[key] if key in kwargs else None

  def update(
      self, **kwargs
  ):
    '''Sets the specified config values'''
    for key in kwargs:
      self.__dict__[key] = kwargs[key]

  def update_from_file(self, config_file: str = None):
    if (config_file == None):
      config_file = self.config_file
    else:
      self.config_file = config_file

    try:
      if self.config_file is not None:
        if config_file.endswith('.json'):
          self.update_from_json(self.config_file)
        elif config_file.endswith('.yaml'):
          self.update_from_yaml(self.config_file)
    except FileNotFoundError:
      print(f'Could not load config file {self.config_file}, continuing...')

  def update_from_json(self, config_file: str):
    with open(config_file, 'r') as file:
      self.update(**json.loads(file.read()))

  def update_from_yaml(self, config_file: str):
    with open(config_file, 'r') as file:
      self.update(**yaml.safe_load(file)) 

  def get_log_level(self) -> int:
    if self.log_level == 'ERROR':
      return logging.ERROR

    if self.log_level == 'WARN' or self.log_level == 'WARNING':
      return logging.WARNING

    if self.log_level == 'INFO':
      return logging.INFO

    if self.log_level == 'DEBUG':
      return logging.DEBUG

    return logging.INFO

  def normalize_paths(self):
    if self.temp_prefix is not None and self.temp_prefix.startswith('.'):
      self.temp_prefix = abspath(self.temp_prefix) + "/"

    if self.destination is not None and self.destination.startswith('.'):
      self.destination = abspath(self.destination) + "/"

CONFIG = Config()