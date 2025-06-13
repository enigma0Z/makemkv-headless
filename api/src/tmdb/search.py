#!/usr/bin/env python3

import logging
from typing import Any
import requests

from src.json_serializable import JSONSerializable
from src.config import CONFIG

logger = logging.getLogger(__name__)

API_HOST_NAME = 'api.themoviedb.org'
WEB_HOST_NAME = 'www.themoviedb.org'
API_VERSION = '3'

class Data(JSONSerializable):
  def __init__(self, data):
    self.data = data

  def __getattr__(self, attr: str):
    try:
      return self.data[attr]
    except KeyError as ex:
      if attr == 'name':
        return self.data['title']
      else:
        raise ex
  
  def json_encoder(self):
    return self.data

class SearchResult (Data):
  def __init__(self, data, content_type):
    super().__init__(data)
    self.content_type = content_type
    self.url = f'https://{WEB_HOST_NAME}/{content_type}/{self.id}'

  def __str__(self):
    return f'{self.id}: {self.name}, {self.url}'


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
    return [SearchResult(result, content) for result in response.json()['results']]
  else:
    return Data(response_json)