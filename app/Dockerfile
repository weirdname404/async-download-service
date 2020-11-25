FROM python:alpine
ENV PYTHONUNBUFFERED 1

RUN apk --no-cache add zip build-base

COPY requirements.txt /tmp/
RUN  pip install -r /tmp/requirements.txt

WORKDIR /app/
COPY . .
