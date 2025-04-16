# snnif

### Dependencies

- `docker` - Required to build and run the Docker containers.
  - This can be installed using Docker Desktop, view the instructions
    [here](https://www.docker.com/products/docker-desktop). For this framework,
    version 28.0.4 was used for testing.
- `python` - Required to urn the framework.
  - This framework was tested with Python 3.12.3.

### Directories

- `protocols` - Contains the Dockerfiles for the protocols
- `src` - Contains the source code for snnif.

### Usage

To run the framework, use the following command:

```bash
source setup.sh
```

This will setup a virtual environment and install the required Python packages.

### Included protocols

Currently, the following protocols are included by default in this framework:

- [FALCON](https://github.com/snwagh/falcon-public)
- [Meteor](https://github.com/Ye-D/Meteor)
- [SecureNN](https://github.com/snwagh/securenn-public)

Chameleon and [ABY³](https://github.com/ladnir/aby3) will likely be added in the
future. It will also be possible to add custom protocols using configuration
files.

#### Configuring a protocol

In order to add a protocol to the framework, two files are required. Inside the
`protocols` directory, add a directory with the name of the protocol. Inside
this directory, add a `Dockerfile` and a `config.json` file.

The `Dockerfile` should contain the instructions to build the Docker image for
the protocol along with the necessary dependencies. An example for the FALCON
protocol:

```dockerfile
# Use Ubuntu 18.04 as the base image
FROM ubuntu:18.04

# Install the necessary dependencies
RUN apt-get update \
    && apt-get install -y \
    git \
    make \
    g++ \
    libssl-dev \
    && rm -r /var/lib/apt/lists/*

# Clone the FALCON repository
RUN git clone https://github.com/snwagh/falcon-public.git Falcon

# Build the FALCON protocol
RUN cd Falcon \
    && make all -j$(nproc)

# Set the working directory to the FALCON directory
WORKDIR Falcon
```

The `config.json` file should contain the configuration for the protocol. It
should be in JSON format and should contain the following fields:

- `run` - The command to run the protocol
- `args` - The arguments to pass to the protocol, this should be a list of
  strings
- `image` - The name of the Docker image to build

### Compatibility

This framework was written and tested on a machine using Ubuntu 24.04.2 LTS with
Python 3.12.3. However, it should be possible to run it on any device with
Python 3 and Docker installed.
