#!/bin/bash

for session in $(ls /run/screen/S-$USER/*.mmh-api-*); do
	pid=$(basename $session | cut -d. -f1)
	kill $pid
done
