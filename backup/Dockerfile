FROM ubuntu:latest

WORKDIR /home

COPY backup.sh /home

RUN apt-get update
RUN apt-get -y install cron wget
RUN touch /var/log/cron.log

RUN wget https://github.com/Backblaze/B2_Command_Line_Tool/releases/latest/download/b2-linux

RUN chmod +x ./b2-linux

RUN (crontab -l ; echo "* * * * * bash backup.sh") | crontab

CMD cron && tail -f /var/log/cron.log