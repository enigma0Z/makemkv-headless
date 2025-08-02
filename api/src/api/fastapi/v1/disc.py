
from src.api.api_response import APIResponse
from src.api.fastapi import json_api
from src.api.fastapi.singletons.singletons import API
from src.api.state import STATE
from src.config import CONFIG
from src.disc import eject_disc
from src.json_serializable import JSONSerializable

@API.get('/api/v1/disc/eject')
@json_api
def get_disc_eject():
  try:
    eject_disc(CONFIG.source)
    STATE.reset_socket()
    # clear_cache('/api/v1/toc')
    return APIResponse("success")
  except Exception as ex:
    return APIResponse("error", ex)