FROM python:latest as python_base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt
RUN mkdir /app

WORKDIR /app
COPY . .
