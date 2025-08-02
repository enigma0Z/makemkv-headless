from fastapi import Response
from src.api import cached_api
from src.api.fastapi import json_api
from src.api.fastapi.singletons.singletons import API

@API.get('/api/v1/cache/clear')
@json_api
def get_clear_cache():
  try:
    cached_api.clear_cache()
    return "success"
  except:
    return Response("failure", status_code=500)