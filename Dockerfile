FROM python:3.8

MAINTAINER Mehdi Sadour

ENV PYTHONUNBUFFERED 1
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /api/