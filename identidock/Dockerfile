FROM python:3.14

RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt 

WORKDIR /app

COPY app /app
COPY cmd.sh /
COPY entrypoint.sh /
RUN chmod +x /cmd.sh /entrypoint.sh

ENV FLASK_APP=identidock.py

EXPOSE 9090 9191
USER uwsgi

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/cmd.sh"]
