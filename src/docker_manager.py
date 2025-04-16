#!/usr/bin/env python3
"""
docker_manager.py

This module manages Docker containers for executing protocols. It provides
functions to build, run, and stop Docker containers. It also handles
communication with the Docker daemon and manages the lifecycle of
containers.
"""

import docker


class DockerManager:
    """
    The manager for Docker containers to build and run protocols.

    This class provides methods to build Docker images, run containers, and
    manage protocol execution inside Docker. It is initialized with a
    configuration dictionary that includes the protocol's name, image, path,
    and run parameters.
    """

    def __init__(self, config):
        """
        Initialize the DockerManager with the protocol name and configuration.

        :param config: Configuration data for the protocol.
        """
        self._container_id = None
        self._protocol_name = config.get("name")
        self._image_name = config.get("image")
        self._run_command = config.get("run")
        self._args = config.get("args", [])
        self._verbose = config.get("verbose", False)
        self._path = config.get("path")
        self._built = config.get("built", False)

    def build_image(self):
        """
        Build the Docker image for the protocol. In case the user has used the
        built flag, this function will check if a build already exists instead.
        """
        if self._built:
            client = docker.from_env()
            try:
                client.images.get(self._image_name)
                if self._verbose:
                    print(
                        f"Image already built, using '{self._image_name}'")
            except docker.errors.ImageNotFound:
                print(f"Image '{self._image_name}' not found.")
                print("Maybe you accidentally added the built flag?")
                exit(1)
            finally:
                client.close()
            return

        if self._verbose:
            print(f"Building Docker image '{self._image_name}'...")

        client = docker.from_env()
        try:
            for line in client.api.build(path=self._path, dockerfile='Dockerfile',
                                         tag=self._image_name, decode=True):
                if 'stream' in line and self._verbose:
                    print(line['stream'].strip())
            if self._verbose:
                print(f"Image '{self._image_name}' built successfully.")
        except docker.errors.BuildError as e:
            print(f"Error building image: {e}")
            exit(1)
        except docker.errors.APIError as e:
            print(f"Error communicating with Docker API: {e}")
            exit(1)
        finally:
            client.close()

    def run_container(self):
        """
        Run the Docker container with the specified command and arguments.
        """
        if self._verbose:
            print(f"Running Docker container '{self._protocol_name}'...")

        client = docker.from_env()
        try:
            if self._verbose:
                print(
                    f"Running command '{self._run_command} {' '.join(self._args)}' in container '{self._protocol_name}'")
            self._container_id = client.containers.run(
                self._image_name,
                command=f"{self._run_command} {' '.join(self._args)}",
                detach=True,
                tty=True,
                auto_remove=True,
                volumes={self._path: {'bind': '/data', 'mode': 'rw'}},
                environment={"PROTOCOL_ARGS": " ".join(self._args)}
            )
            if self._verbose:
                print(f"Container '{self._protocol_name}' is running.")
                # Print the docker output
                for line in self._container_id.logs(stream=True):
                    print(line.decode('utf-8'), end='')
        except docker.errors.ContainerError as e:
            print(f"Error running container: {e}")
            exit(1)
        except docker.errors.APIError as e:
            print(f"Error communicating with Docker API: {e}")
            exit(1)
        finally:
            client.close()
