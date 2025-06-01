from json import loads

class Config:
  def __init__(self):
    '''Initialize a config object'''

    self.tmdb_token = None
    self.makemkvcon_path = None
    self.source_drive = None
    self.dest_path = None
    self.temp_prefix = None
    self.loaded = False

  def load(
      self, 
      tmdb_token: str, 
      makemkvcon_path: str, 
      source_drive: str, 
      dest_path: str, 
      temp_prefix: str | None = None
  ):
    '''Initialize a config object'''

    self.tmdb_token = tmdb_token
    self.makemkvcon_path = makemkvcon_path
    self.source_drive = source_drive
    self.dest_path = dest_path
    self.temp_prefix = temp_prefix
    self.loaded = True

  def from_json_file(self, filename: str):
    with open(filename, 'r') as file:
      self.load(**loads(file.read()))

CONFIG: Config = None