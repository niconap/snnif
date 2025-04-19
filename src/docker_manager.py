#!/usr/bin/env python3
"""
docker_manager.py

This module manages Docker containers for executing protocols. It provides
functions to build, run, and stop Docker containers. It also handles
communication with the Docker daemon and manages the lifecycle of
containers.
"""

import tarfile
import io
import os

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
        self._container = None
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
            for line in client.api.build(
                path=self._path,
                dockerfile='Dockerfile',
                tag=self._image_name,
                decode=True
            ):
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

    def run_command(self, command):
        """
        Run the specified command inside the Docker container.

        :return: The output of the command execution.
        """
        if self._container:
            if self._verbose:
                print(f"Running command '{command}' in container...")

            try:
                output = self._container.exec_run(
                    command,
                    environment={"PROTOCOL_ARGS": " ".join(self._args)},
                    stream=True,
                    tty=True
                )

                output_lines = []
                for line in output.output:
                    decoded = line.decode('utf-8').rstrip()
                    if self._verbose:
                        print(decoded)
                    output_lines.append(decoded)

                return "\n".join(output_lines)
            except docker.errors.APIError as e:
                print(f"Error executing command: {e}")
                exit(1)
            except Exception as e:
                print(f"Unexpected error: {e}")
                exit(1)
        else:
            print("Container is not running. Cannot execute command.")
            exit(1)
        return None

    def copy_file(self, src, dest):
        """
        Copy a file from the host to the Docker container.

        :param src: Source file path on the host.
        :param dest: Destination directory path inside the container.
        """
        if self._container:
            if self._verbose:
                print(f"Copying file '{src}' to container '{dest}'...")

            try:
                # Create a tar archive in memory
                tar_stream = io.BytesIO()
                with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                    tar.add(src, arcname=os.path.basename(src))
                tar_stream.seek(0)

                # Send the tar archive to the container
                self._container.put_archive(dest, tar_stream)
                if self._verbose:
                    print(f"File '{src}' copied successfully to '{dest}'.")
            except docker.errors.APIError as e:
                print(f"Error copying file: {e}")
                exit(1)
            except Exception as e:
                print(f"Unexpected error: {e}")
                exit(1)
        else:
            print("Container is not running. Cannot copy file.")
            exit(1)

    def run_container(self):
        """
        Start the Docker container with the specified configuration without running any command.

        :return: The active Docker container object.
        """
        if self._verbose:
            print(f"Starting Docker container '{self._protocol_name}'...")

        client = docker.from_env()
        try:
            container = client.containers.run(
                self._image_name,
                detach=True,
                tty=True,
                auto_remove=False,
                volumes={self._path: {'bind': '/data', 'mode': 'rw'}},
            )

            if self._verbose:
                print(f"Container '{self._protocol_name}' is running.")

            self._container = container
        except docker.errors.ContainerError as e:
            print(f"Error starting container: {e}")
            exit(1)
        except docker.errors.APIError as e:
            print(f"Error communicating with Docker API: {e}")
            exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)

    def stop_container(self):
        """
        Stop and remove the Docker container if it is running.

        :return: True if the container was stopped successfully, False
        otherwise.
        """
        if self._container:
            try:
                if self._verbose:
                    print(
                        f"Stopping Docker container '{self._protocol_name}'..."
                    )
                self._container.stop()
                self._container.remove(force=True)
                if self._verbose:
                    print((f"Container '{self._protocol_name}' stopped and "
                           "removed."))
                return True
            except docker.errors.APIError as e:
                print(f"Error stopping container: {e}")
                return False
        return False
