import json
import logging

from flask import Response, request
from src.api.json_api import json_api, json_api
from src.api.singletons.singletons import API
from src.api.singletons.state import STATE

logger = logging.getLogger(__name__)

@API.get('/api/v1/state')
@API.get('/api/v1/state/')
@json_api
def get_state():
  return STATE

@API.get('/api/v1/state/<path:path>')
@json_api
def get_state_select(path: str):
  path_parts = [ path_part for path_part in path.split("/") if path_part != '' ]
  selected_data = STATE.data
  try:
    output_object = {}
    next_object = output_object
    for index, path_part in enumerate(path_parts):
      selected_data = selected_data[path_part] # Descend into state tree

      if index == len(path_parts) - 1: # Last object
        next_object[path_part] = selected_data
      else:
        next_object[path_part] = {}
        next_object = next_object[path_part]

    return output_object
  except KeyError as ex:
    logger.error(f'Unable to find key {ex}')
    return ({}, 400)
  
@API.put('/api/v1/state')
@json_api
def put_state():
  try:
    data = json.loads(request.data.decode('utf-8'))
    STATE.data['redux']['rip'] = data['redux']['rip']
    return data
  except:
    return ("failure", 400)

@API.get('/api/v1/state.reset')
@json_api
def reset_state():
  try:
    STATE.reset_all()
    return ("success", 202)
  except:
    return ("failure", 500)

@API.get('/api/v1/state.reset/socket')
@json_api
def reset_state_socket():
  try:
    STATE.reset_socket()
    return ("success", 202)
  except:
    return ("failure", 500)
    