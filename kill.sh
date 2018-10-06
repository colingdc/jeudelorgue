#!/usr/bin/env bash

for pid in $(ps aux | grep gunicorn | grep 8001 | awk '{print $2}'); do kill ${pid}; done

