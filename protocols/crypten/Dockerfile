FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y \
    git \
    cmake \
    wget \
    nethogs \
    python3 \
    python3-pip \
    && rm -r /var/lib/apt/lists/*

RUN mkdir deeplearning && mkdir deeplearning/projects
RUN git clone --depth 1 https://github.com/niconap/CrypTen.git deeplearning/projects/crypten

RUN cd deeplearning/projects/crypten \
    && sed -i 's/sklearn/scikit-learn/g' requirements.txt \
    && pip3 install -r requirements.txt \
    && pip3 install -r requirements.examples.txt

COPY ILSVRC2012_devkit_t12.tar.gz /nn_data/
COPY ILSVRC2012_img_val.tar /nn_data/

WORKDIR /
