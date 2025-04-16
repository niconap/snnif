"""
docker_manager.py

This module manages Docker containers for executing protocols. It provides
functions to build, run, and stop Docker containers. It also handles
communication with the Docker daemon and manages the lifecycle of
containers.
"""


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
