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

from .json_api import json_api
from .singletons import *
from .v1 import *

@API.route('/')
@json_api
def index():
    return json.dumps({'foo': 'bar', 'bin': 'baz'})