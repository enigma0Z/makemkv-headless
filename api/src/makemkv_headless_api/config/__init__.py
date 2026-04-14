import json
import logging
import yaml

from os.path import abspath

from makemkv_headless_api.models.config import ConfigModel, LogLevelStr

class Config(ConfigModel):
  keys: list[str] = []

  def __str__(self):
    return json.dumps(self.__dict__)

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

    if config_file.endswith('.json'):
      self.update_from_json(config_file)
    elif config_file.endswith('.yaml'):
      self.update_from_yaml(config_file)

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
    if self.temp_prefix.startswith('.'):
      self.temp_prefix = abspath(self.temp_prefix) + "/"

    if self.destination.startswith('.'):
      self.destination = abspath(self.destination) + "/"

CONFIG = Config()