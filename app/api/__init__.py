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
import logging
from threading import Thread
from flask import Flask, request

from app.api.interface import ThreadQueueInterface
from rip import rip_titles
from sort import ShowInfo, SortInfo
from toc import TOC

logger = logging.getLogger(__name__)
interface = ThreadQueueInterface()

class State:
    def __init__(self):
        self.ripping = False
        self.sorting = False
        self.copying = False 
    
state = State()

app = Flask(__name__)

@app.route('/')
def index():
    return json.dumps({'foo': 'bar', 'bin': 'baz'})

@app.route('/api/v1/toc')
def get_toc():
    toc = TOC(interface=interface)
    toc.get_from_disc()
    return toc.to_json()

@app.route('/api/v1/tmdb/show')
def get_tmdb_show():
    pass

@app.route('/api/v1/tmdb/movie')
def get_tmdb_movie():
    pass
