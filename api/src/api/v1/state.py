import json
from math import ceil

from fastapi import APIRouter, HTTPException

from src.api.api_response import APIResponse, PaginatedAPIResponse

import logging

from src.api.state import STATE
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/state")

DEFAULT_PAGE_SIZE = 10

def get_state_by_path(path: str, page=None, page_size=None, filter_keys: list[str]=[]):
  path_parts = [ path_part for path_part in path.split("/") if path_part != '' ]
  num_pages = None
  selected_data = STATE.model_dump()
  try:
    output_object = {}
    next_object = output_object
    logger.debug(f'path_parts: {path_parts}')
    for index, path_part in enumerate(path_parts):
      logger.debug(f'path_part: {path_part}')
      if type(selected_data) in [tuple, list]:
        logger.debug(f'path_part has integer indexes')
        path_part = int(path_part)

      selected_data = selected_data[path_part] # Descend into state tree

      if index == len(path_parts) - 1: # Last object
        if (
          type(page) == int and type(page_size) == int
        ):
          logger.debug(f'path_part is the last in the list')
          if type(selected_data) == list and page != None and page_size != None:
            logger.debug(f'paginating; page: {page}, size: {page_size}')
            num_pages = ceil(len(selected_data)/page_size)
            selected_data = selected_data[page*page_size:page*page_size+page_size]
            for filter_key in filter_keys:
              for selected_item in selected_data:
                if filter_key in selected_item:
                  selected_item[filter_key] = "<FILTERED>"
          else:
            raise ValueError(f'Data at path {path} cannot be paginated')

        next_object[path_part] = selected_data
      else:
        next_object[path_part] = {}
        next_object = next_object[path_part]

    if (num_pages != None):
      return PaginatedAPIResponse(page=page, page_size=page_size, num_pages=num_pages, status="success", data=output_object)
    else:
      return APIResponse(status="success", data=output_object)
  except KeyError as ex:
    logger.error(f'Unable to find key {ex}')
    raise ValueError(f'Cannot find data at path {path}')

@router.get('')
@router.get('/')
def get_state():
  return STATE

@router.get('/{state_path:path}')
def get_state_select(state_path: str):
  try:
    return get_state_by_path(state_path)
  except Exception as ex:
    raise HTTPException(500, APIResponse(status="error"))

@router.get('/api/v1/state.paginated/<path:path>')
def get_state_paginated(path: str):
  try:
    page = int(request.args['page']) if 'page' in request.args else 0
    page_size = int(request.args['page_size']) if 'page_size' in request.args else DEFAULT_PAGE_SIZE
    filter_keys = request.args['filter_keys'].split(',') if 'filter_keys' in request.args else []
    return get_state_by_path(path, page, page_size, filter_keys)

  except Exception as ex:
    logger.error(ex)
    return (APIResponse("error", f'{ex}'), 400)

  
# @router.put('/api/v1/state')
# def put_state():
#   try:
#     data = json.loads(request.data.decode('utf-8'))
#     STATE.data['redux']['rip'] = data['redux']['rip']
#     return data
#   except:
#     return ("failure", 400)

@router.get('.reset')
def reset_state():
  try:
    STATE.reset_all()
    return APIResponse(status="success")
  except:
    return ("failure", 500)

@router.get('.reset/socket')
def reset_state_socket():
  try:
    STATE.reset_socket()
    return APIResponse(status="success")
  except Exception as ex:
    raise HTTPException(500, APIResponse(status="error"))
    