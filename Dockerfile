FROM ubuntu

WORKDIR /usr/app
COPY . .

RUN apt-get update
RUN apt-get -y install python3 && apt-get -y install python3-pip
RUN pip3 install -r requirements.txt