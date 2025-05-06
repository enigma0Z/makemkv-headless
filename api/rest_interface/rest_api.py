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
from flask import Flask

app = Flask(__name__)
@app.route('/')
def index():
    return json.dumps({'foo': 'bar', 'bin': 'baz'})

@app.route('/api/v1/rip/dvd')

@app.route('/api/v1/rip/blu-ray')

@app.route('/api/v1/get_toc')

@app.route('/api/v1/sort/movie')

@app.route('/api/v1/sort/show')

@app.route('/api/v1/store_content')