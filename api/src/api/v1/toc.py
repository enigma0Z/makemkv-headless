from functools import lru_cache
import logging
from threading import Lock
from traceback import format_exc

from fastapi import APIRouter

from src.api.api_response import APIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
# from src.message.toc_complete_message_event import TOCCompleteMessageEvent
from src.toc import TOC

logger = logging.getLogger(__name__)

lock = Lock()

router = APIRouter(prefix="/toc")

# @lru_cache
def get_toc_from_disc(source):
  toc = TOC()
  toc.get_from_disc(source)
  return toc

@router.get('')
@router.get('/')
async def get_toc():
  try:
    with lock:
      toc = get_toc_from_disc(CONFIG.source)
      STATE.redux.toc = toc
      return APIResponse("success", toc)
  except Exception as ex:
    logger.error(format_exc())
    raise APIException(500, APIError("error", ex))

@router.get('.cache.clear')
async def toc_clear_cache():
  try:
    get_toc_from_disc.cache_clear()
  except Exception as ex:
    raise APIException(500, APIError("error", ex))

@router.get('.cache.info')
async def toc_clear_cache():
  return get_toc_from_disc.cache_info()