import logging
import os
from threading import Lock, Thread
from flask import Response, request

# from rip_titles import rip_titles
from src.config import CONFIG
from src.sort import *
from src.rip_titles.rip_titles import rip_titles
from src.api.json_api import json_serializable_api
from src.api.singletons.singletons import API, INTERFACE

logger = logging.getLogger(__name__)

LOCK = Lock()

class APIRequest:
    def __init__(self, destination: str, rip_all: bool, sort_info: dict[str, str]):
        '''
        * `destination`: Library path where this rip will go. ex:
          `"main/dvd/movies"`. Automatically concatenated onto the end of the
          configured base path
        '''
        self.rip_all = rip_all
        self.sort_info: SortInfo | ShowInfo
        self.destination: str = destination
        exceptions: list[Exception] = []
        for clazz in [ShowInfo, SortInfo]: # type: ignore
          try: 
                self.sort_info = clazz(**sort_info)
                return 
          except Exception as ex:
                exceptions.append(ex)
        
        raise(Exception(exceptions))

class APIResponse(JSONSerializable):
    def __init__(self, status):
        self.status = status

@API.post('/api/v1/rip')
@json_serializable_api
def post_rip():
    # extract SortInfo from post data
    data = APIRequest(**request.json)
    logger.debug(data)

    def rip_thread_fn():
        logger.debug(f'rip_thread_fn(), {CONFIG}')
        with LOCK:
            toc = TOC(interface=INTERFACE)
            toc.get_from_disc(CONFIG.source)

            rip_titles(
                source=CONFIG.source,              # From config
                dest_path=os.path.join(CONFIG.destination, data.destination),
                sort_info=data.sort_info, # From post data
                toc=toc,                 # Not sending this
                rip_all=data.rip_all,     # From post data
                interface=INTERFACE,      # From singletons
                temp_prefix=CONFIG.temp_prefix # From config
            )

    if not LOCK.locked():
        logger.debug('not LOCK.locked()')
        Thread(
            target=rip_thread_fn,
            daemon=True
        ).start()

        return APIResponse("started")

    else:
        logger.debug('LOCK.locked()')
        return (
            APIResponse("in progress"),
            Response(status=208)
        )
        