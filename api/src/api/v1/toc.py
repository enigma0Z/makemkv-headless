import logging
from src.api.singletons.state import STATE
from src.config import CONFIG
from src.toc import TOC
from src.api.json_api import json_api
from src.api.singletons.singletons import API, INTERFACE

logger = logging.getLogger(__name__)

@API.route('/api/v1/toc')
@json_api
def get_toc():
    toc = TOC(interface=INTERFACE)
    toc.get_from_disc(CONFIG.source)
    STATE.data['redux']['toc'] = toc
    return toc