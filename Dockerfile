FROM python:3.11.2

COPY core /core
WORKDIR /core


RUN pip install -r /core/requirements.txt