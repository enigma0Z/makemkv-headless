from fastapi import Response
from makemkv_headless.api import cached_api
from makemkv_headless.api.fastapi import json_api
from makemkv_headless.api.fastapi import API

@API.get('/api/v1/cache/clear')
@json_api
def get_clear_cache():
  try:
    cached_api.clear_cache()
    return "success"
  except:
    return Response("failure", status_code=500)