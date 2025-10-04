from functools import lru_cache
import logging
from threading import Lock
from traceback import format_exc

from fastapi import APIRouter, BackgroundTasks

from src.api.api_response import GenericAPIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
from src.interface import get_interface
from src.models.socket import TocStatusMessage
from src.toc import Toc

class TocError(Exception): ...

logger = logging.getLogger(__name__)

lock = Lock()
toc = Toc()

router = APIRouter(prefix="/toc")

# @lru_cache
async def get_toc_from_disc(source):
  with lock:
    await toc.get_from_disc(source)
    STATE.redux.toc = toc
    get_interface().send(TocStatusMessage(state="complete"))
    return toc

@router.get('')
@router.get('/')
async def get_toc():
  try:
    toc = await get_toc_from_disc(CONFIG.source)
    failures = toc.get_failures()

    if len(failures) > 0: 
      raise TocError(failures)

    STATE.redux.toc = toc
    return APIResponse("success", toc)
  except TocError as ex:
    logger.error(ex.args[0])
    raise APIException(404, failures)
  except Exception as ex:
    logger.error(format_exc())
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.async')
async def get_toc_async(background_tasks: BackgroundTasks):
  try:
    if lock.locked():
      return APIResponse("in progress")
    else:
      background_tasks.add_task(get_toc_from_disc, CONFIG.source)
      return APIResponse("started", toc)
  except TocError as ex:
    logger.error(ex.args[0])
  except Exception as ex:
    logger.error(format_exc())
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.async.status')
async def get_toc_async(background_tasks: BackgroundTasks):
  if lock.locked():
    return APIResponse("in progress")
  else:
    return APIResponse("done", toc)

@router.get('.cache.clear')
async def toc_clear_cache():
  try:
    get_toc_from_disc.cache_clear()
  except Exception as ex:
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.cache.info')
async def toc_clear_cache():
  return get_toc_from_disc.cache_info()