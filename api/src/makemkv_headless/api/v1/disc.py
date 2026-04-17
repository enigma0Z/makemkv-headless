
import logging
from traceback import format_exc
from fastapi import APIRouter, HTTPException
from makemkv_headless.api.api_response import APIResponse
from makemkv_headless.api.state import STATE
from makemkv_headless.config import CONFIG
from makemkv_headless.disc import eject_disc
from makemkv_headless.interface.async_queue_interface import INTERFACE

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