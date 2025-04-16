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
    A class to manage Docker containers for executing protocols.
    """

    def __init__(self, config):
        """
        Initialize the DockerManager with the protocol name and configuration.

        :param protocol_name: Name of the protocol.
        :param config: Configuration data for the protocol.
        """
        self.container_id = None
        self.protocol_name = config.get("name")
        self.image_name = config.get("image")
        self.run_command = config.get("run")
        self.args = config.get("args", [])
        self.verbose = config.get("verbose", False)
        self.path = config.get("path")
        self.built = config.get("built", False)

    def build_image(self):
        """
        Build the Docker image for the protocol.
        """
        if self.built:
            client = docker.from_env()
            try:
                client.images.get(self.image_name)
                if self.verbose:
                    print(
                        f"Image already built, using '{self.image_name}'")
            except docker.errors.ImageNotFound:
                print(f"Image '{self.image_name}' not found.")
                print("Maybe you accidentally added the built flag?")
                exit(1)
            finally:
                client.close()
            return

        if self.verbose:
            print(f"Building Docker image '{self.image_name}'...")

        client = docker.from_env()
        try:
            for line in client.api.build(path=self.path, dockerfile='Dockerfile',
                                         tag=self.image_name, decode=True):
                if 'stream' in line and self.verbose:
                    print(line['stream'].strip())
            if self.verbose:
                print(f"Image '{self.image_name}' built successfully.")
        except docker.errors.BuildError as e:
            print(f"Error building image: {e}")
            exit(1)
        except docker.errors.APIError as e:
            print(f"Error communicating with Docker API: {e}")
            exit(1)
        finally:
            client.close()
