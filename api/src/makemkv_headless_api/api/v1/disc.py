
import logging
from traceback import format_exc
from fastapi import APIRouter, HTTPException
from src.api.api_response import APIResponse
from src.api.state import STATE
from src.config import CONFIG
from src.disc import eject_disc
from src.interface.async_queue_interface import INTERFACE

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/disc")

@router.get('/eject')
@router.get('/eject/')
async def get_disc_eject():
  try:
    await eject_disc(CONFIG.source, INTERFACE)
    STATE.reset_socket()
    return APIResponse(status="success")
  except Exception as ex:
    logger.error(format_exc())
    raise HTTPException(500, APIResponse(status="error", data=f'{type(ex)} = {ex}').model_dump())