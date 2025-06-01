from json import dumps, loads

from json_serializable import JSONSerializable

class Config(JSONSerializable):
  keys: list[str] = []

  def __init__(self):
    '''Initialize a blank config object'''
    if (len(Config.keys) > 0):
      raise Exception("Config has already been initialized")

    self.tmdb_token: str = None
    self.makemkvcon_path: str = None
    self.source: str = None
    self.destination: str  = None
    self.log_level: str = None
    self.temp_prefix: str = None

    Config.keys = self.__dict__.keys()

  def __str__(self):
    return dumps(self.__dict__)

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

  def update_from_json(self, filename: str):
    with open(filename, 'r') as file:
      self.update(**loads(file.read()))

CONFIG = Config()