from api.json_api import json_serializable_api
from api.singletons import API
from config import CONFIG

@API.get('/api/v1/config')
@json_serializable_api
def get_config():
  return CONFIG

@API.get('/api/v1/config/reload')
@json_serializable_api
def get_config_reload():
  CONFIG.update_from_file()
  return CONFIG