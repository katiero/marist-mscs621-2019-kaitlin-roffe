FROM ubuntu:16.04

RUN apt-get update 
RUN apt-get install -y build-essential python-pip python-dev
RUN pip install --upgrade pip

RUN mkdir -p /opt/giftLog
ADD . /opt/giftLog
RUN pip install -r /opt/giftLog/requirements.txt

WORKDIR /opt/giftLog
EXPOSE 5000

CMD python server.py
