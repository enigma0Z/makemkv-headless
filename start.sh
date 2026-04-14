#!/bin/bash

SCREEN="false"
LISTEN_PORT=""

if [[ "$1" == "screen" ]]; then
  SCREEN="true"; shift
  LISTEN_PORT="$1"; shift
fi

if [[ "$SCREEN" == "true" ]]; then
  screen -dmS mmh-api-$LISTEN_PORT uv --project api run mmh_api --listen-port $LISTEN_PORT "$@"
else
  uv --project api run mmh_api "$@"
fi