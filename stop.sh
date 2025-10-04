#!/bin/bash

pids=$(/run/screen/s-$USER/makemkv-batch-*)
kill $pids