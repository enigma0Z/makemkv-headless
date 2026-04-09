import logging
from fastapi import APIRouter
from src.api.api_response import APIResponse
from src.config import CONFIG

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/config")

@router.get('')
@router.get('/')
async def get_config():
  return APIResponse(status="success", data=CONFIG)

@router.get('.reload')
def get_config_reload():
  CONFIG.update_from_file()
  return APIResponse(status="success", data=CONFIG)