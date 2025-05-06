# snnif

### Dependencies

- `docker` - Required to build and run the Docker containers.
  - This can be installed using Docker Desktop, view the instructions
    [here](https://www.docker.com/products/docker-desktop). This framework was
    tested with Docker 28.0.4.
- `python` - Required to run the framework.
  - This framework was tested with Python 3.12.3.
- [_Scaphandre_](https://github.com/hubblo-org/scaphandre) - Required to measure
  the power consumption of the protocol.
  - This must be installed on the **host device**. It can be installed using
    the command below:
    ```bash
    sudo apt install scaphandre
    ```

### Directories

- `protocols` - Contains the Dockerfiles for the protocols
- `src` - Contains the source code for snnif.

### Usage

In order to use the framework, the necessary dependencies need to be installed
on the system. This can be achieved by using a virtual Python environment. By
using the command below, such a virtual environment will be created and
activated and the dependencies will be installed.

```bash
source setup.sh
```

`source` is used here to activate the virtual environment automatically.

In case you are managing your virtual environments in a different way, for
example by using Anaconda, you can create your own virtual environment and
install the dependencies using `pip`:

```bash
pip install -r requirements.txt
```

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
the protocol along with the necessary dependencies. **It is important to install
`nethogs`, `python3` and `python3-pip` in the container.** An example for the
_FALCON_ protocol:

```dockerfile
# Use Ubuntu 18.04 as the base image, if necessary, choose a different version
FROM ubuntu:18.04

# Install the necessary dependencies, make sure to include nethogs
RUN apt-get update \
  && apt-get install -y \
  git \
  make \
  g++ \
  libssl-dev \
  nethogs \
  python3 \
  python3-pip \
  && rm -r /var/lib/apt/lists/*

# Clone the FALCON repository
RUN git clone https://github.com/snwagh/falcon-public.git Falcon

# Build the FALCON protocol
RUN cd Falcon \
  && make all -j$(nproc)

# Set the working directory to the FALCON directory
WORKDIR Falcon
```

By default, the framework assumes the `WORKDIR` is the root directory of the
container. It will look for the first line that specifies `WORKDIR`, and changes
this default value if one is found.

The `config.json` file should contain the configuration for the protocol. It
should be in JSON format and should contain the following fields:

- `run` - The command to run the protocol, this includes its arguments
  - In case it is necessary to run multiple instances of the protocol (e.g. one
    for each party), you can run each one in a sub-shell. See the configuration
    file for _Meteor_ for an example.
- `image` - The name of the Docker image to build
- `execfile` - The name of the file to execute in the container (usually this
  is `<name>.out`, but that depends on the protocol). If you are not sure what
  this should be, run the protocol once with this field set to some dummy value
  and check `results/nethogs_<num>.txt`, scroll down to the bottom and look for
  a line that has the name in it. For example, here the name should be
  `Meteor.out`:
  ```
  Refreshing:
  ./Meteor.out/34/0	1860.98	0
  ./Meteor.out/35/0	1953.95	0
  ./Meteor.out/36/0	1395.53	0
  unknown TCP/0/0	0	0
  ```

#### Extra measurements

In case the protocol added to the framework gives extra measurements, it is
possible to take these as well. In this case, the protocol must output the
wanted measurements to a file in the Docker container. This could be done by
the protocol itself or by redirecting its output.

In order to enable extra measurements, two additional fields are required in
the configuration file. `extra` specifies if extra measurements should be taken,
this should be a boolean value of `true`. `extra_files` specifies which files
should be taken from the Docker container to get the extra measurements.

Then, inside `src/extra`, create a new Python file with the name of the
protocol. This name should match the name of the directory in `protocols`. For
example, for `protocols/meteor`, a file called `src/extra/meteor.py` is
required. This new Python file should specify two methods:
`retrieve_data(docker_manager, config)` for retrieving the files and
`process_data(data)` to process this data. The latter can be left empty using
a `pass` statement.

### Compatibility

This framework was written and tested on a machine using Ubuntu 24.04.2 LTS with
Python 3.12.3. However, it should be possible to run it on any device with
Python 3 and Docker installed. _Scaphandre_ should also be available for the
host device, which is available for
[Linux distributions](https://hubblo-org.github.io/scaphandre-documentation/tutorials/installation-linux.html)
and [Windows](https://hubblo-org.github.io/scaphandre-documentation/tutorials/installation-windows.html).
However, this framework was not tested on Windows, so it is possible it does not
work as expected.
