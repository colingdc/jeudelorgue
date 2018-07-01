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

for pid in $(ps aux | grep gunicorn | grep ${port} | awk '{print $2}'); do kill ${pid}; done
