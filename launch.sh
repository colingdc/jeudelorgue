#!/usr/bin/env bash

instance=$(head -n 1 instance.txt)

if [ ${instance} == "production" ]
then
    port=8002
fi

if [ ${instance} == "development" ]
then
    port=8001
fi

nohup gunicorn manage:app -b localhost:${port} >/dev/null &
