import json
import yaml

from src.json_serializable import JSONSerializable

class Config(JSONSerializable):
  keys: list[str] = []

  def __init__(self):
    '''Initialize a blank config object'''
    if (len(Config.keys) > 0):
      raise Exception("Config has already been initialized")

    self.filename: str = None
    self.tmdb_token: str = None
    self.makemkvcon_path: str = None
    self.source: str = None
    self.destination: str  = None
    self.log_level: str = None
    self.temp_prefix: str = None
    self.frontend: str = None

    Config.keys = self.__dict__.keys()

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
    for key in Config.keys:
      if key in kwargs:
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