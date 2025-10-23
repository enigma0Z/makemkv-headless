#!/bin/bash

if [[ "$1" == "api" ]]; then
	screen -R makemkv-headless-api
elif [[ "$1" == "web" ]]; then
	screen -R makemkv-headless-web
fi;