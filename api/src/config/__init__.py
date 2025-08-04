import json
import yaml

from src.models.config import ConfigModel

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

  def update_from_file(self, filename: str = None):
    if (filename == None):
      filename = self.filename
    else:
      self.filename = filename

    if filename.endswith('.json'):
      self.update_from_json(filename)
    elif filename.endswith('.yaml'):
      self.update_from_yaml(filename)

  def update_from_json(self, filename: str):
    with open(filename, 'r') as file:
      self.update(**json.loads(file.read()))

  def update_from_yaml(self, filename: str):
    with open(filename, 'r') as file:
      self.update(**yaml.safe_load(file)) 

CONFIG = Config()