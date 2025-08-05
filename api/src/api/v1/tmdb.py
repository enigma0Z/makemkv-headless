from functools import lru_cache
from fastapi import APIRouter

from src.api.api_response import APIResponse
from src.tmdb import configuration, search

router = APIRouter(prefix="/tmdb")

@router.get('/show')
@lru_cache
def get_tmdb_show(q: str):
    response = search('tv', q)
    return APIResponse(status="success", data=response)

@router.get('/movie')
@lru_cache
def get_tmdb_movie(q: str):
    response = search('movie', q)
    return APIResponse(status="success", data=response)

@router.get('/configuration')
@lru_cache
def get_tmdb_configuration():
    response = configuration()
    return APIResponse(status="success", data=response)