FROM python:3.12.4

WORKDIR /home

ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y portaudio19-dev
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*


RUN chmod -R 777 /home

COPY requirements.txt .

RUN pip install -r requirements.txt
