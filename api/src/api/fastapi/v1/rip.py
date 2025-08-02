import logging
import os
from threading import Lock, Thread
from typing import Union

from pydantic import BaseModel

# from rip_titles import rip_titles
from src.api.api_response import APIResponse
from src.api.fastapi import json_api
from src.api.fastapi.singletons.singletons import API, INTERFACE
from src.api.state import STATE
from src.config import CONFIG
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.models.sort import ShowInfoModel, SortInfoModel
from src.rip_titles.threaded import RipTitlesThread
from src.toc import TOC

logger = logging.getLogger(__name__)

LOCK = Lock()
RIP_THREAD: RipTitlesThread = None

class RequestModel(BaseModel):
    destination: str
    rip_all: bool
    sort_info: SortInfoModel | ShowInfoModel

@API.post('/api/v1/rip')
@json_api
def post_rip(data: RequestModel):
    global LOCK, RIP_THREAD
    # extract SortInfo from post data

    logger.debug(data)

    def rip_thread_fn():
        global RIP_THREAD
        logger.debug(f'rip_thread_fn(), {CONFIG}')
        with LOCK:
            STATE.reset_socket()
            toc = TOC(interface=INTERFACE)
            toc.get_from_disc(CONFIG.source)

            RIP_THREAD = RipTitlesThread(
                kwargs={
                    "source": CONFIG.source,              # From config
                    "dest_path": os.path.join(CONFIG.destination, data.destination),
                    "sort_info": data.sort_info, # From post data
                    "toc": toc,                 # Not sending this
                    "rip_all": data.rip_all,     # From post data
                    "interface": INTERFACE,      # From singletons
                    "temp_prefix": CONFIG.temp_prefix # From config
                }
            )

            RIP_THREAD.start()

    if not LOCK.locked():
        logger.debug('not LOCK.locked()')
        Thread(
            target=rip_thread_fn,
            daemon=True
        ).start()

        return APIResponse("started")

    else:
        logger.debug('LOCK.locked()')
        return (APIResponse("in progress"), 200)
        
@API.get('/api/v1/rip.stop')
@json_api
def get_rip_stop():
    try:
        RIP_THREAD.stop()
        INTERFACE.send(RipStartStopMessageEvent(state="stop"))
        return ("success", 200)
    except:
        return ("failure", 500)