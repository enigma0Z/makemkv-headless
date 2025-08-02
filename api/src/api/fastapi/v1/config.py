from src.api.fastapi import json_api
from src.api.fastapi.singletons.singletons import API
from src.config import CONFIG


@API.get('/api/v1/config')
@json_api
def get_config():
  return CONFIG

@API.get('/api/v1/config/reload')
@json_api
def get_config_reload():
  CONFIG.update_from_file()
  return CONFIG