#!/usr/bin/env python3

from _TOKEN import BEARER_TOKEN
from typing import Any
import requests

API_HOST_NAME = 'api.themoviedb.org'
WEB_HOST_NAME = 'www.themoviedb.org'
API_VERSION = '3'

class Data:
  def __init__(self, data):
    self.data = data

  def __getattr__(self, attr: str):
    return self.data[attr]

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
    headers = { 'Authorization': f'Bearer {BEARER_TOKEN}' },
    params = { 'query': query }
  )

  return [SearchResult(result, content) for result in response.json()['results']]