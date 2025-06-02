from functools import wraps
from typing import Callable

from flask import Response

from json_serializable import JSONSerializable

def json_serializable_api(function: Callable[[], JSONSerializable]):
  @wraps(function)
  def decorated_function():
    return Response(
      function().to_json(),
      content_type="application/json; charset=utf-8"
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