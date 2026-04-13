FROM python:3.11-alpine3.23

COPY requirements.txt /temp/requirements.txt
COPY freelancer /freelancer
WORKDIR /freelancer
EXPOSE 8000

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password freelancer-user

USER freelancer-user
