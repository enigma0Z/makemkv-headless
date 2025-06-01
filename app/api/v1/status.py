import logging
from api.json_api import json_serializable_api
from api.singletons import API, INTERFACE
from json_serializable import JSONSerializable

logger = logging.getLogger(__name__)

class Response(JSONSerializable):
  def __init__(self):
    self.messages = []
    while INTERFACE.queue.qsize() > 0:
      self.messages.append(INTERFACE.queue.get_nowait())

@API.get('/api/v1/status')
@json_serializable_api
def get_status():
  return Response()