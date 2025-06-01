import logging
from app.api import app, interface
from app.api.json_serializable import JSONSerializable

logger = logging.getLogger(__name__)

class Response(JSONSerializable):
  def __init__(self):
    self.messages = []
    while interface.queue.qsize() > 0:
      self.messages.append(interface.queue.get_nowait())

@app.get('/api/v1/status')
def status():
  return Response().to_json()