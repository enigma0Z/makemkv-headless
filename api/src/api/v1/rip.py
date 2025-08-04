from asyncio import Lock, Task, create_task
import logging
import os

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.api_response import APIError, APIException, APIResponse
from src.api.state import STATE
from src.config import CONFIG
from src.interface.async_queue_interface import INTERFACE
from src.message.rip_start_stop_message_event import RipStartStopMessageEvent
from src.models.sort import ShowInfoModel, SortInfoModel
from src.rip_titles.rip_titles import rip_titles
from src.toc import TOC

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/rip')

lock: Lock = Lock()
rip_task: Task | None = None

class RequestModel(BaseModel):
  destination: str
  rip_all: bool
  sort_info: SortInfoModel | ShowInfoModel

async def rip_task_fn(data: RequestModel):
  logger.debug(f'rip_thread_fn(), {CONFIG}')
  with lock:
    STATE.reset_socket()
    toc = TOC(interface=INTERFACE)
    toc.get_from_disc(CONFIG.source)

    rip_titles(
      source=CONFIG.source,
      dest_path=os.path.join(CONFIG.destination, data.destination),
      sort_info=data.sort_info,
      toc=toc,
      rip_all=data.rip_all,
      interface=INTERFACE,
      temp_prefix=CONFIG.temp_prefix
    )

@router.post('/api/v1/rip')
async def post_rip(data: RequestModel):
  logger.debug(data)

  if rip_task == None or rip_task.done():
    rip_task = create_task(rip_task_fn(data))
    return APIResponse("started")

  else:
    return APIResponse("in progress")
    
@router.get('/api/v1/rip.stop')
async def get_rip_stop():
  try:
    if rip_task != None:
      if not rip_task.done():
        rip_task.cancel()
        INTERFACE.send(RipStartStopMessageEvent(state="stop"))
        return APIResponse(status="in progress")

    return APIResponse(status="stopped")
    
  except Exception as ex:
    raise APIException(500, APIError("error", ex))