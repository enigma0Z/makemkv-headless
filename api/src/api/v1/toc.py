from src.config import CONFIG
from src.toc import TOC
from src.api.json_api import json_serializable_api
from src.api.singletons.singletons import API, INTERFACE

@API.route('/api/v1/toc')
@json_serializable_api
def get_toc():
    toc = TOC(interface=INTERFACE)
    toc.get_from_disc(CONFIG.source)
    return toc