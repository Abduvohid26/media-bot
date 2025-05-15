FROM python:3.12.4

WORKDIR /home

ENV PYTHONUNBUFFERED=1


RUN chmod -R 777 /home

COPY requirements.txt .

RUN pip install -r requirements.txt
