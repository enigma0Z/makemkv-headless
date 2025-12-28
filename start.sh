#!/bin/bash

api_port="$1"; shift
web_ip="$1"; shift
web_port="$1"; shift

if [[ -z "$api_port" ]]; then
	api_port=4000
fi

if [[ -z "$web_port" ]]; then
	web_port=3000
fi

screen -dmS makemkv-headless-api-$api_port ./api.sh --port $api_port --frontend "http://${web_ip}:${web_port}" "@$"
screen -dmS makemkv-headless-web-$web_port ./web.sh --port $web_port
