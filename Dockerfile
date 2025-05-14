FROM python:3.12.4

WORKDIR /home


RUN chmod -R 777 /home

COPY requirements.txt .

RUN pip install -r requirements.txt
