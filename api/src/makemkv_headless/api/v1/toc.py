from asyncio import Event
from functools import lru_cache
import logging
from threading import Lock
from traceback import format_exc

from fastapi import APIRouter, BackgroundTasks

from makemkv_headless.api.api_response import GenericAPIError, APIException, APIResponse
from makemkv_headless.api.state import STATE
from makemkv_headless.config import CONFIG
from makemkv_headless.interface import get_interface
from makemkv_headless.models.socket import TocStatusMessage
from makemkv_headless.toc import Toc
from makemkv_headless.util import cancellable_async

class TocError(Exception): ...

logger = logging.getLogger(__name__)

LOCK = Lock()
CANCEL = Event()

router = APIRouter(prefix="/toc")

async def get_toc_from_disc(source = CONFIG.source):
  with LOCK:
    toc = Toc()
    STATE.reset_toc()
    STATE.reset_rip_indexes() # Reset which indexes are selected
    STATE.reset_socket() # Reset which indexes are complete
    logger.info('Getting TOC...')
    await cancellable_async(toc.get_from_disc(source), CANCEL)
    STATE.toc.source = toc.source
    get_interface().send(TocStatusMessage(state="complete"))
    return toc

@router.get('')
@router.get('/')
async def get_toc():
  if LOCK.locked():
    return APIResponse("in progress")
  else:
    if STATE.toc.source is not None:
      return APIResponse(status='success', data=STATE.toc)
    else:
      return APIResponse(status='stopped')


@router.get('.start')
async def get_toc_start(background_tasks: BackgroundTasks):
  if LOCK.locked():
    return APIResponse("in progress")
  else:
    background_tasks.add_task(get_toc_from_disc)
    return APIResponse("started")

@router.get('.status')
async def get_toc_status():
  if LOCK.locked():
    return APIResponse("in progress")
  else:
    return APIResponse("done")

@router.get('.stop')
async def toc_get_stop():
  if LOCK.locked():
    CANCEL.set()
    return APIResponse("in progress")
  else:
    return APIResponse("done")