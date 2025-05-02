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
RUN git clone --depth 1 https://github.com/facebookresearch/CrypTen.git deeplearning/projects/crypten

RUN cd deeplearning/projects/crypten \
    && sed -i 's/sklearn/scikit-learn/g' requirements.txt \
    && pip3 install -r requirements.txt \
    && pip3 install -r requirements.examples.txt

RUN wget https://github.com/raminrasoulinezhad/torchvision/raw/65e236ec28fc9182b40c14f6cecfa7237a6e0c1c/ILSVRC2012_devkit_t12.tar.gz \
    -O /tmp/ILSVRC2012_devkit_t12.tar.gz

RUN wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate \
    -O /tmp/ILSVRC2012_img_val.tar

WORKDIR /
