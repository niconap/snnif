FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
    git \
    make \
    g++ \
    libssl-dev \
    && rm -r /var/lib/apt/lists/*

RUN git clone https://github.com/Ye-D/Meteor.git Meteor

RUN cd Meteor \
    && make all -j$(nproc)

WORKDIR Meteor
