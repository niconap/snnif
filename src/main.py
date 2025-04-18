#!/usr/bin/env python3
"""
main.py

This script is the main entry point for the protocol execution. It handles
command-line arguments and validates the protocol configuration. This
information is passed to the Docker manager.
"""

import argparse
import os
import json

from docker_manager import DockerManager


def parse_config(config_path):
    """
    Parse the configuration file. In case of an invalid configuration, exit the
    program with an error message.

    @param config_path: Path to the configuration file.
    @return: Parsed configuration data.
    """
    try:
        with open(config_path, 'r') as file:
            config_data = file.read()
            return json.loads(config_data)
    except FileNotFoundError:
        print(f"Configuration file '{config_path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON format in '{config_path}'.")
        exit(1)


def validate_config(config):
    """
    Validate the configuration data. In case of an invalid configuration, exit
    the program with an error message.

    @param config: Parsed configuration data.
    """
    required_keys = ["run", "image"]
    for key in required_keys:
        if key not in config or config[key] == '':
            print(f"Missing required key '{key}' in configuration.")
            exit(1)


def parse_arguments():
    """
    Parse command-line arguments.

    @return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="snnif")
    parser.add_argument("--name", "-n", type=str, help="Protocol name")
    parser.add_argument("--config", "-c", type=str,
                        help="Path to the configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--built", "-b", action="store_true",
                        help=(
                            "Specify if the Docker image has already been "
                            "built"
                        ))
    return parser.parse_args()


def get_protocol_path(protocol_name):
    """
    Get the protocol path based on the protocol name.

    @param protocol_name: Name of the protocol.
    @return: Path to the protocol folder.
    """
    protocol_path = os.path.join(os.getcwd(), "protocols", protocol_name)
    if not os.path.exists(protocol_path):
        print(f"Protocol folder '{protocol_path}' does not exist")
        exit(1)
    return protocol_path


def get_config_path(protocol_path, config_arg):
    """
    Get the configuration file path.

    @param protocol_path: Path to the protocol folder.
    @param config_arg: Command-line argument for the config file.
    @return: Path to the configuration file.
    """
    if config_arg:
        config_path = os.path.abspath(config_arg)
    else:
        config_path = os.path.join(protocol_path, "config.json")

    if not os.path.exists(config_path):
        print(f"Error: protocol config file '{config_path}' does not exist")
        exit(1)

    return config_path


def display_verbose_info(protocol_name, config):
    """
    Display verbose information about the protocol and configuration.

    @param protocol_name: Name of the protocol.
    @param config: Configuration data.
    """
    print("== Protocol name ==")
    print(protocol_name)
    print()
    print("== Selected configuration ==")
    for key, value in config.items():
        print(f"{key}\t\t{value}")
    print()


def run_protocol(config):
    """
    Run the protocol using Docker.

    @param config: Configuration data.
    """
    docker_manager = DockerManager(config)
    docker_manager.build_image()
    docker_manager.run_container()
    time1 = docker_manager.run_command("date +%s%3N")
    docker_manager.copy_file(
        os.path.join(os.path.dirname(__file__), "protocol_manager.py"),
        "Meteor"  # Copy to the working directory
    )
    docker_manager.run_command(
        f'python3 protocol_manager.py --command "{config["run"]}"')
    time2 = docker_manager.run_command("date +%s%3N")
    docker_manager.stop_container()
    print((int(time2) - int(time1)) / 1000.0, "second(s) elapsed")


if __name__ == "__main__":
    args = parse_arguments()

    if not args.name:
        print("Error: missing protocol name")
        exit(1)

    protocol_path = get_protocol_path(args.name)
    config_path = get_config_path(protocol_path, args.config)

    config = parse_config(config_path)
    validate_config(config)
    config["name"] = args.name
    config["path"] = protocol_path
    config["verbose"] = args.verbose
    config["built"] = args.built

    if args.verbose:
        display_verbose_info(args.name, config)

    run_protocol(config)
