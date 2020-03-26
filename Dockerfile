from python:3.7-alpine
maintainer Flavio Monteiro

env PYTHONUNBUFFERED 1

copy ./requirements.txt /requirements.txt
run apk add --update --no-cache postgresql-client
run apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
run pip install -r /requirements.txt
run apk del .tmp-build-deps

run mkdir /app
workdir /app
copy ./app /app

run adduser -D user
user user