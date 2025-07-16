#!/bin/bash

function run_api() {
  cd api

  if [ ! -d .venv ]; then
    python3 -m venv .venv
  fi

  source .venv/bin/activate
  pip install -r requirements.txt

  python3 -m src $@ &
  echo $!
}

function run_web() {
  cd web
  npm install
  npm run dev $@ &
  echo $!
}

./api.sh &
API_PID=$!

./web.sh &
WEB_PID=$!

function ctrl_c() {
  kill -9 $WEB_PID
  kill -9 $API_PID
}

echo "API: $API_PID"
echo "WEB: $WEB_PID"

trap ctrl_c INT

wait $API_PID $WEB_PID
kill -9 $API_PID $WEB_PID
