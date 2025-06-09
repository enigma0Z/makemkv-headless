from functools import wraps
from typing import Callable

from flask import Response
from json_serializable import JSONSerializable

JSON_CONTENT_TYPE = "application/json; charset=utf-8"

def json_serializable_api(function: Callable[[], JSONSerializable | tuple[JSONSerializable, Response]]):
  @wraps(function)
  def decorated_function():
    api_response = function()
    if isinstance(api_response, tuple):
      json, response = api_response
      assert json is not None
      assert response is not None

      response.response = json.to_json()
      response.content_type = JSON_CONTENT_TYPE
      return response
    else:
      json = api_response
      return Response(
        response=json.to_json(),
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
