

import json
from flask import request
from api.singletons import API
from api.json_api import json_serializable_api
from api import json_api
from tmdb.search import search

@API.get('/api/v1/tmdb/show')
@json_serializable_api
def get_tmdb_show():
    response = search('tv', request.args['q'])
    return response

@API.get('/api/v1/tmdb/movie')
@json_serializable_api
def get_tmdb_movie():
    response = search('movie', request.args['q'])
    return response