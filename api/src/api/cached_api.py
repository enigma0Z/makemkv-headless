from functools import wraps
import logging
from flask import request

logger = logging.getLogger(__name__)

CACHE = {}

def cached_api(function):
  global CACHE
  @wraps(function)
  def cached_api_wrapper(*args, **kwargs):
    if request.url in CACHE:
      logger.info(f'Using cached response for {request.url}')
      return CACHE[request.url]
    else:
      response = function(*args, **kwargs)
      CACHE[request.url] = response
      return response
  return cached_api_wrapper

def clear_cache():
  global CACHE
  CACHE = {}