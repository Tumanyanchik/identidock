#!/bin/bash

set -e

echo "Starting identidock"

docker run -d --restart=always --name dnmonster amouat/dnmonster:1.0
docker run -d --restart=always --name redis redis:8.6.2-alpine
docker run -d --restart=always --name identidock --link dnmonster --link redis -e ENV=PROD tumanyan/identidock:newest
docker run -d --restart=always --name proxy --link identidock:identidock -p 80:80 \
	-e NGINX_HOST=192.168.30.53 -e NGINX_PROXY=http://identidock:9090 \
	tumanyan/proxy:1.0
echo "Started"
