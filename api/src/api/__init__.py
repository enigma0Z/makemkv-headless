#!/usr/bin/env python3
'''
Rest / JSON interface + API

Endpoints

1  Get TOC
2  Rip Disc
3  Sort Content
4  Store Content
'''

import json

from src.api.json_api import json_api
from src.api.singletons.singletons import *
from src.api.v1 import *

@API.route('/')
@json_api
def index():
    return json.dumps({'foo': 'bar', 'bin': 'baz'})