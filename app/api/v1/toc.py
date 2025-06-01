

from api.json_api import json_serializable_api
from api.singletons import API, INTERFACE
from config import CONFIG
from toc import TOC

@API.route('/api/v1/toc')
@json_serializable_api
def get_toc():
    toc = TOC(interface=INTERFACE)
    toc.get_from_disc(CONFIG.source)
    return toc