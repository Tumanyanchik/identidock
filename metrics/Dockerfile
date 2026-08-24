FROM alpine:3.22

RUN apk add --no-cache alertmanager=0.28.1-r8 gettext

COPY alertmanager.tmpl /etc/alertmanager/alertmanager.tmpl

ENTRYPOINT ["/bin/sh", "-c"]

CMD ["chown -R 65534:65534 /alertmanager && envsubst < /etc/alertmanager/alertmanager.tmpl > /etc/alertmanager/alertmanager.yml && /usr/bin/alertmanager --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/alertmanager --web.listen-address=0.0.0.0:9093"]
