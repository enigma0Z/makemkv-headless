import json

from functools import wraps
from typing import Callable
from flask import Response

from src.json_serializable import JSONSerializable

JSON_CONTENT_TYPE = "application/json; charset=utf-8"

def json_serializable_api(function: Callable[[], JSONSerializable | tuple[JSONSerializable, Response]]):
  @wraps(function)
  def decorated_function():
    api_response = function()
    if isinstance(api_response, tuple):
      json_data, response = api_response
      assert json_data is not None
      assert response is not None

      response.response = json.dumps(json_data)
      response.content_type = JSON_CONTENT_TYPE
      return response
    else:
      json_data = None
      if isinstance(api_response, list):
        json_data = json.dumps([value.json_encoder() for value in api_response])
      else:
        json_data = api_response.to_json()
      return Response(
        response=json_data,
        content_type=JSON_CONTENT_TYPE
      )

  return decorated_function

def json_api(function: Callable[[any], any]):
  @wraps(function)
  def decorated_function(*args, **kwargs):
    return Response(
      function(*args, **kwargs),
      content_type="application/json; charset=utf-8"
    )
  return decorated_function
