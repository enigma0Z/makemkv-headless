from fastapi import APIRouter

from src.interface import get_interface
from src.message.base_message_event import BaseMessageEvent

router = APIRouter(prefix="/queue")

@router.get('/put')
async def queue_put(message: str):
  await get_interface().send(BaseMessageEvent(message=message))