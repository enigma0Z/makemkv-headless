from asyncio import Lock, Task, create_task
import logging
import os

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.api.api_response import APIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.rip_titles.asyncio import rip_titles
from src.sort import ShowInfo, SortInfo
from src.toc import TOC

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/rip')

rip_task: Task | None = None

LOCK = Lock()

class RequestModel(BaseModel):
  destination: str
  rip_all: bool
  sort_info: SortInfo | ShowInfo

async def rip_task_fn(data: RequestModel):
  async with LOCK:
    logger.debug(f'rip_task_fn(), {rip_task}')
    STATE.reset_socket()
    toc = TOC()
    await toc.get_from_disc(CONFIG.source)
    await rip_titles(
      source=CONFIG.source,
      dest_path=os.path.join(CONFIG.destination, data.destination),
      sort_info=data.sort_info,
      toc=toc,
      rip_all=data.rip_all,
      temp_prefix=CONFIG.temp_prefix
    )

@router.post('')
@router.post('/')
async def post_rip(data: RequestModel, background_tasks: BackgroundTasks):
  logger.debug(data)

  if not LOCK.locked():
    background_tasks.add_task(rip_task_fn, data)
    return APIResponse("started")

  else:
    return APIResponse("in progress")
    
@router.get('.stop')
async def get_rip_stop():
  global rip_task
  try:
    if rip_task != None:
      if not rip_task.done():
        rip_task.cancel()
        INTERFACE.send(RipStartStopMessageEvent(state="stop"))
        return APIResponse(status="in progress")

    return APIResponse(status="stopped")
    
  except Exception as ex:
    raise APIException(500, APIError("error", ex))