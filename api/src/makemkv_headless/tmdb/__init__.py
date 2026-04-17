#!/usr/bin/env python3

import logging
from typing import Any
import requests

from makemkv_headless_api.api.api_response import APIException, GenericAPIError
from makemkv_headless_api.config import CONFIG
from makemkv_headless_api.models.tmdb import TMDBConfigurationModel, TMDBMovieSearchResultModel, TMDBShowSearchResultModel

logger = logging.getLogger(__name__)

API_HOST_NAME = 'api.themoviedb.org'
WEB_HOST_NAME = 'www.themoviedb.org'
API_VERSION = '3'

def search(content, query):
  content = content.lower()
  url = f'https://{API_HOST_NAME}/{API_VERSION}/search/{content.lower()}'
  response = requests.get(
    url = url,
    headers = { 'Authorization': f'Bearer {CONFIG.tmdb_token}' },
    params = { 'query': query }
  )

  response_json = response.json()

  if ('results' in response_json): 
    if content == 'movie':
      return [TMDBMovieSearchResultModel(**result) for result in response.json()['results']]
    elif content == 'tv':
      return [TMDBShowSearchResultModel(**result) for result in response.json()['results']]
  else:
    return [] # No results

def configuration():
  url = f'https://{API_HOST_NAME}/{API_VERSION}/configuration'
  response = requests.get(
    url = url,
    headers = { 'Authorization': f'Bearer {CONFIG.tmdb_token}' },
  )

  try:
    return TMDBConfigurationModel(**response.json())
  except Exception as ex: 
    raise APIException(500, GenericAPIError("error", ex))