import logging
from src.api.json_api import json_serializable_api
from src.api.singletons.singletons import API
from src.api.singletons.state import STATE

logger = logging.getLogger(__name__)

@API.get('/api/v1/status')
@json_serializable_api
def get_status():
  return STATE
  