from fastapi import APIRouter

from makemkv_headless_api.interface import get_interface
from makemkv_headless_api.message.base_message_event import BaseMessageEvent

router = APIRouter(prefix="/queue")

@router.get('/put')
async def queue_put(message: str):
  await get_interface().send(BaseMessageEvent(message=message))