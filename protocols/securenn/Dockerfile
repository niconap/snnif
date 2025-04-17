FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
    git \
    make \
    g++ \
    libssl-dev \
    xterm \
    && rm -r /var/lib/apt/lists/*

RUN git clone https://github.com/snwagh/securenn-public.git SecureNN

RUN cd SecureNN \
    && make

WORKDIR SecureNN
