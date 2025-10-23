from asyncio import Lock, Task, create_task
import logging
import os

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.api.api_response import GenericAPIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
from src.interface import get_interface
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.models.socket import RipStartStopMessage
from src.rip_titles.asyncio import rip_titles
from src.sort import ShowInfo, SortInfo
from src.toc import Toc

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

async def rip_task_fn(data: RequestModel):
  async with LOCK:
    logger.debug(f'rip_task_fn(), {rip_task}')
    STATE.reset_socket()
    toc = Toc()
    await toc.get_from_disc(CONFIG.source)
    await rip_titles(
      source=CONFIG.source,
      dest_path=os.path.join(CONFIG.destination, data.destination),
      sort_info=data.sort_info,
      toc=toc,
      rip_all=data.rip_all,
      temp_prefix=CONFIG.temp_prefix
    )

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
  global rip_task
  try:
    if rip_task != None:
      if not rip_task.done():
        rip_task.cancel()
        interface.send(RipStartStopMessageEvent(state="stop"))
        return APIResponse(status="in progress")

    return APIResponse(status="stopped")
    
  except Exception as ex:
    raise APIException(500, GenericAPIError("error", ex))