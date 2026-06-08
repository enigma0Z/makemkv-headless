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

# @lru_cache
async def get_toc_from_disc(source):
  with LOCK:
    toc = Toc()
    # STATE.reset_rip_indexes() # Reset which indexes are selected
    STATE.reset_socket() # Reset which indexes are complete
    logger.info('Getting TOC...')
    await cancellable_async(toc.get_from_disc(source), CANCEL)
    STATE.toc = toc
    get_interface().send(TocStatusMessage(state="complete"))
    return toc

@router.get('')
@router.get('/')
@router.get('.async') # Deprecated
async def get_toc_async(background_tasks: BackgroundTasks):
  try:
    if LOCK.locked():
      return APIResponse("in progress")
    else:
      background_tasks.add_task(get_toc_from_disc, CONFIG.source)
      return APIResponse("started")
  except TocError as ex:
    logger.error(ex.args[0])
  except Exception as ex:
    logger.error(format_exc())
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.status')
@router.get('.async.status') # Deprecated
async def get_toc_async_status():
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

@router.get('.cache.clear')
async def toc_clear_cache():
  try:
    get_toc_from_disc.cache_clear()
  except Exception as ex:
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.cache.info')
async def toc_clear_cache():
  return get_toc_from_disc.cache_info()