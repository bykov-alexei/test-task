FROM python:3.9.13

COPY . /server
WORKDIR /server

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

CMD /bin/bash start.sh