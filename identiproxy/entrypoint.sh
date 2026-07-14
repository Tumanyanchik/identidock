#!/bin/sh
set -e

sed -i "s|{{ NGINX_HOST }}|$NGINX_HOST|g; s|{{ NGINX_PROXY }}|$NGINX_PROXY|g" \
   /etc/nginx/conf.d/default.conf
cat /etc/nginx/conf.d/default.conf
exec "$@"
