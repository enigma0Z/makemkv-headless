from asyncio import Event, Lock, Task
import asyncio
import logging
import os

from fastapi import APIRouter, BackgroundTasks
from makemkv_headless.util import cancellable_async
from pydantic import BaseModel

from makemkv_headless.api.api_response import GenericAPIError, APIException, APIResponse
from makemkv_headless.api.state import STATE
from makemkv_headless.config import CONFIG
from makemkv_headless.interface import get_interface
from makemkv_headless.models.socket import RipStartStopMessage
from makemkv_headless.rip_titles.asyncio import rip_titles
from makemkv_headless.sort import ShowInfo, SortInfo
from makemkv_headless.toc import Toc

class RequestModel(BaseModel):
  destination: str
  rip_all: bool
  sort_info: SortInfo | ShowInfo

class ResponseModel(BaseModel):
  request: RequestModel

interface = get_interface()
logger = logging.getLogger(__name__)
router = APIRouter(prefix='/rip')

rip_task: Task | None = None
rip_request: RequestModel | None = None

LOCK = Lock()
CANCEL = Event()

async def rip_task_fn(data: RequestModel):
  assert CONFIG.source is not None
  assert CONFIG.destination is not None
  assert CONFIG.temp_prefix is not None

  async with LOCK:
    logger.debug(f'rip_task_fn(), {rip_task}')
    STATE.reset_socket()
    STATE.socket.rip.started = True
    toc = Toc()

    try:
      await cancellable_async(toc.get_from_disc(CONFIG.source), CANCEL)
      await cancellable_async(
        rip_titles(
          source=CONFIG.source,
          dest_path=os.path.join(CONFIG.destination, data.destination),
          sort_info=data.sort_info,
          toc=toc,
          rip_all=data.rip_all,
          temp_prefix=CONFIG.temp_prefix
        ),
        CANCEL
      )
    except asyncio.CancelledError:
      logger.info('Rip cancelled')
    finally:
      get_interface().send(RipStartStopMessage(state="stop"))

@router.post('')
@router.post('/')
async def post_rip(data: RequestModel, background_tasks: BackgroundTasks):
  logger.debug(data)
  global rip_request 
  rip_request = data

  if not LOCK.locked():
    background_tasks.add_task(rip_task_fn, data)
    return APIResponse("started", rip_request)

  else:
    return APIResponse("in progress", rip_request)

@router.get('')
@router.get('/')
async def get_rip():
  if not LOCK.locked():
    return APIResponse("stopped", rip_request)

  else:
    return APIResponse("in progress", rip_request)
    
@router.get('.stop')
async def get_rip_stop():
  try:
    if LOCK.locked():
      CANCEL.set()
      get_interface().send(RipStartStopMessage(state="stop"))
      return APIResponse(status="in progress")

    return APIResponse(status="stopped")
    
  except IndexError as ex:
    raise APIException(500, GenericAPIError("error", Exception("No rip task found")))

  except Exception as ex:
    raise APIException(500, GenericAPIError("error", ex))