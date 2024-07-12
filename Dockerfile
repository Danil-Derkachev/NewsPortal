FROM python:3.8-alpine3.19

RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev

ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./ ./

WORKDIR /app/news_portal
EXPOSE 8000
CMD python3 ./manage.py runserver 0.0.0.0:8000
