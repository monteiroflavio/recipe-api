from python:3.7-alpine
maintainer Flavio Monteiro

env PYTHONUNBUFFERED 1

copy ./requirements.txt /requirements.txt
run pip install -r /requirements.txt

run mkdir /app
workdir /app
copy ./app /app

run adduser -D user
user user