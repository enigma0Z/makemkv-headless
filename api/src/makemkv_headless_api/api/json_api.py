import json

from functools import wraps
import logging
from typing import Callable
from fastapi import Response

from src.json_serializable import JSONSerializable

logger = logging.getLogger(__name__)

JSON_CONTENT_TYPE = "application/json; charset=utf-8"

type serializable_api_response = JSONSerializable | str | dict | list[any]

def json_api(
    function: Callable[
      [], 
      serializable_api_response
        | list[serializable_api_response]
        | tuple[serializable_api_response, Response]
        | tuple[list[serializable_api_response], Response]
    ]
):
  @wraps(function)
  def decorated_function(*args, **kwargs):
    api_response = function(*args, **kwargs)
    response_data: str = None
    response_object: Response = None

    if isinstance(api_response, tuple):
      response_data, response_object = api_response
      assert response_data is not None
      assert response_object is not None
      if isinstance(response_object, int):
        response_object = Response(status_code=response_object)

      assert isinstance(response_object, Response)
    else:
      response_data = api_response
      response_object = Response()

    json_data = JSONSerializable.dumps(response_data)
      
    response_object.body = json_data
    response_object.media_type = JSON_CONTENT_TYPE

    return response_object

  return decorated_function