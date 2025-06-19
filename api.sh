#!/bin/bash
cd api

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r api/requirements.txt

python3 -m src $@