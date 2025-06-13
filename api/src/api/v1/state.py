import json
import logging

from flask import request
from src.api.json_api import json_api, json_serializable_api
from src.api.singletons.singletons import API
from src.api.singletons.state import STATE

logger = logging.getLogger(__name__)

@API.get('/api/v1/state')
@json_serializable_api
def get_status():
  return STATE
  
@API.put('/api/v1/state')
@json_api
def put_state():
  data = json.loads(request.data.decode('utf-8'))
  STATE.data['redux']['rip'] = data['redux']['rip']
  return request.data.decode('utf-8')