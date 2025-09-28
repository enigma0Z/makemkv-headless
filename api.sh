#!/bin/bash
cd api

rm -rvf .venv
python3.13 -m venv .venv

source .venv/bin/activate
pip install -r requirements.txt

exec python3 -m src.api_main
