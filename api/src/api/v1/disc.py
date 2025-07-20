
from src.api.json_api import json_api
from src.api.singletons.singletons import API
from src.api.singletons.state import STATE
from src.config import CONFIG
from src.disc import eject_disc
from src.json_serializable import JSONSerializable

class APIResponse(JSONSerializable):
  def __init__(self, status, exception=None):
    self.status = status
    self.exception = exception

@API.get('/api/v1/disc/eject')
@json_api
def get_disc_eject():
  try:
    eject_disc(CONFIG.source)
    STATE.reset_socket()
    return APIResponse("success")
  except Exception as ex:
    return APIResponse("failure", ex)