from functools import lru_cache
import logging
from threading import Lock
from traceback import format_exc

from fastapi import APIRouter

from src.api.api_response import GenericAPIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
# from src.message.toc_complete_message_event import TOCCompleteMessageEvent
from src.toc import TOC

class TOCError(Exception): ...

logger = logging.getLogger(__name__)

lock = Lock()

router = APIRouter(prefix="/toc")

# @lru_cache
async def get_toc_from_disc(source):
  toc = TOC()
  await toc.get_from_disc(source)
  return toc

@router.get('')
@router.get('/')
async def get_toc():
  try:
    with lock:
      toc = await get_toc_from_disc(CONFIG.source)
      failures = toc.get_failures()

      if len(failures) > 0: 
        raise TOCError(failures)

      STATE.redux.toc = toc
      return APIResponse("success", toc)
  except TOCError as ex:
    logger.error(ex.args[0])
    raise APIException(404, failures)
  except Exception as ex:
    logger.error(format_exc())
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.cache.clear')
async def toc_clear_cache():
  try:
    get_toc_from_disc.cache_clear()
  except Exception as ex:
    raise APIException(500, GenericAPIError("error", ex))

@router.get('.cache.info')
async def toc_clear_cache():
  return get_toc_from_disc.cache_info()