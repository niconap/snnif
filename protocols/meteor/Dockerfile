FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
    git \
    make \
    g++ \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -r /var/lib/apt/lists/*

RUN git clone https://github.com/Ye-D/Meteor.git Meteor

RUN cd Meteor \
    && make all -j$(nproc)

RUN pip3 install scapy

WORKDIR Meteor
