from flask import request

from src.api.cached_api import cached_api
from src.api.json_api import json_api
from src.api.singletons.singletons import API

from src.tmdb import configuration, search

@API.get('/api/v1/tmdb/show')
@cached_api
@json_api
def get_tmdb_show():
    response = search('tv', request.args['q'])
    return response

@API.get('/api/v1/tmdb/movie')
@cached_api
@json_api
def get_tmdb_movie():
    response = search('movie', request.args['q'])
    return response

@API.get('/api/v1/tmdb/configuration')
@cached_api
@json_api
def get_tmdb_configuration():
    response = configuration()
    return response