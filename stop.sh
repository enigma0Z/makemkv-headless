#!/bin/bash

for session in $(ls /run/screen/S-$USER/*.makemkv-headless-*); do
	pid=$(basename $session | cut -d. -f1)
	kill $pid
done
