#!/bin/bash

cd web
npm install
exec npm run dev -- $@