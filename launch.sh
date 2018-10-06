#!/usr/bin/env bash

nohup gunicorn manage:app -b localhost:8001 >/dev/null &

