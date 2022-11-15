FROM python:3.8.5-alpine
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY ./requirements.txt .
COPY ./app /app

RUN set -e; apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers mariadb-dev python3-dev postgresql-dev;
RUN pip install --upgrade pip && pip install -r requirements.txt && adduser --disabled-password --no-create-home app

USER app