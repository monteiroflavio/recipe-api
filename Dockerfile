from python:3.7-alpine
maintainer Flavio Monteiro

env PYTHONUNBUFFERED 1

copy ./requirements.txt /requirements.txt
run apk add --update --no-cache postgresql-client jpeg-dev
run apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
run pip install -r /requirements.txt
run apk del .tmp-build-deps

run mkdir /app
workdir /app
copy ./app /app

run mkdir -p /vol/web/media
run mkdir -p /vol/web/static

run adduser -D user
run chown -R user:user /vol/
run chmod -R 755 /vol/web
user user