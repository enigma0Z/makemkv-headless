import logging
from threading import Lock, Thread
from time import sleep

from src.api.api_response import APIResponse
from src.api.singletons.state import STATE
from src.config import CONFIG
from src.message.toc_complete_message_event import TOCCompleteMessageEvent
from src.toc import TOC
from src.api.json_api import json_api
from src.api.singletons.singletons import API, INTERFACE

logger = logging.getLogger(__name__)

LOCK = Lock()
LOADED_TOC: TOC = TOC(interface=INTERFACE)

@API.get('/api/v1/toc')
@json_api
def get_toc():
    global LOCK
    with LOCK:
        toc = TOC(interface=INTERFACE)
        def toc_thread_fn():
            toc.get_from_disc(CONFIG.source)

        thread = Thread(target=toc_thread_fn, daemon=True)
        thread.start()
        while thread.is_alive():
            sleep(0.1)
        
        STATE.data['redux']['toc'] = toc
        return toc

@API.get('/api/v1/toc/<action>')
@json_api
def get_toc_async(action):
    def toc_thread_fn():
        global LOCK, LOADED_TOC
        with LOCK:
            LOADED_TOC = TOC(interface=INTERFACE)
            LOADED_TOC.get_from_disc(CONFIG.source)
            STATE.data['redux']['toc'] = LOADED_TOC
            INTERFACE.send(TOCCompleteMessageEvent(toc=LOADED_TOC))

    if LOCK.locked():
        return APIResponse("in progress")
    elif action == 'load':
        Thread(
            target=toc_thread_fn,
            daemon=True
        ).start()

        return APIResponse("started")
    elif action == 'poll':
        return APIResponse("done", data=LOADED_TOC)
    else:
        return (APIResponse("error", f'Unrecognized action {action}'), 500)