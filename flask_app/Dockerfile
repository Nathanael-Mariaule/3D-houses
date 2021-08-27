FROM python:3.8.5-slim-buster
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y libgl1-mesa-glx libgomp1
RUN apt-get clean && \ 
    rm -rf /var/lib/apt/lists/*
COPY . /flask_app
WORKDIR /flask_app
RUN pip install -r requirements.txt

