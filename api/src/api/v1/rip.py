import logging
import os
from threading import Thread
from flask import request
from api.singletons import API, INTERFACE

# from rip_titles import rip_titles
from config import CONFIG
from rip_titles.rip_titles import rip_titles
from sort import *

logger = logging.getLogger(__name__)

class Request:
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

@API.post('/api/v1/rip')
def post_rip():
    # extract SortInfo from post data
    data = Request(**request.json)

    # start rip in a thread and assign it an id
    Thread(
        kwargs={
            "source": None,              # From config
            "dest_path": os.path.join(CONFIG.destination, data.destination),
            "sort_info": data.sort_info, # From post data
            "toc": None,                 # Not sending this
            "rip_all": data.rip_all,     # From post data
            "interface": INTERFACE,      # From singletons
            "temp_prefix": None          # From config
        },
        target=rip_titles,
        daemon=True
    ).start()