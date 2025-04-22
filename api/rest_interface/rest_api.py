#!/usr/bin/env python3

import json
from flask import Flask

app = Flask(__name__)
@app.route('/')
def index():
    return json.dumps({'foo': 'bar', 'bin': 'baz'})