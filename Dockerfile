# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update
RUN apt-get install -y redis
RUN apt-get install -y celery
WORKDIR /binder
RUN python -m venv /opt/venv
ENV PATH="/home/openhabian/env/bin:$PATH"
COPY requirements.txt /binder
RUN pip install -r requirements.txt
ENV PATH="/home/openhabian/env/bin:$PATH"
COPY . /binder