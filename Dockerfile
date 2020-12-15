FROM ubuntu

WORKDIR /usr/app
COPY . .
COPY run.sh /usr/app/run.sh
RUN chmod +x /usr/app/run.sh

RUN apt-get update
RUN apt-get -y install python3 && apt-get -y install python3-pip
RUN pip3 install -r requirements.txt

RUN /usr/app/run.sh
