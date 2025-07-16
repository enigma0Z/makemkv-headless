#!/bin/bash
cd api

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

exec python3 -m src --api $@