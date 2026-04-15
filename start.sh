#!/bin/bash

SCREEN="false"
DEV="false"
API_PORT=""
WEB_PORT=""

if [[ "$1" == "screen" ]]; then
  SCREEN="true"; shift
  WEB_PORT="$1"; shift
fi

if [[ "$1" == "dev" ]]; then
  DEV="true"; shift
  API_PORT="$1"; shift
  WEB_PORT="$1"; shift
fi

if [[ "$SCREEN" == "true" ]]; then
  screen -dmS mmh-api-$API_PORT uv --project api run mmh_api --listen-port $API_PORT "$@"
elif [[ "$DEV" == "true" ]]; then
  WEB_PID=""
  API_PID=""
  cleanup() {
    echo "Cleaning up"
    set -x
    kill $WEB_PID
    kill $API_PID
    set +x
  }

  uv --project api run mmh_api \
    --listen-port $API_PORT "$@" \
    --cors-origin http://127.0.0.1:3000 \
    --cors-origin http://localhost:3000 &
  API_PID=$!

  export VITE_BACKEND_PORT=$API_PORT
  cd web
  npm run dev -- --port 3000
  WEB_PID=$!

  trap 'cleanup' SIGINT
  wait $API_PID 
  wait $WEB_PID
else
  uv --project api run mmh_api "$@"
fi