from flask import Response, request

from src.api import cached_api
from src.api.json_api import json_api
from src.api.singletons.singletons import API

@API.get('/api/v1/cache/clear')
@json_api
def get_clear_cache():
  try:
    cached_api.clear_cache()
    return "success"
  except:
    return Response("failure", status=500)