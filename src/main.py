#!/usr/bin/env python3
"""
main.py

This script is the main entry point for the protocol execution. It handles
command-line arguments and validates the protocol configuration. This
information is passed to the Docker manager.
"""

import argparse
import os

import utils


def parse_arguments():
    """
    Parse command-line arguments.

    :return: Parsed arguments.
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
    parser.add_argument("--iterations", "-i", type=int,
                        default=1, help="Number of iterations to run")
    parser.add_argument("--max-top", "-m", type=int, default=0,
                        help="Maximum Scaphandre ranking")
    return parser.parse_args()


def get_protocol_path(protocol_name):
    """
    Get the protocol path based on the protocol name.

    :param protocol_name: Name of the protocol.
    :return: Path to the protocol folder.
    """
    protocol_path = os.path.join(os.getcwd(), "protocols", protocol_name)
    if not os.path.exists(protocol_path):
        print(f"Protocol folder '{protocol_path}' does not exist")
        exit(1)
    return protocol_path


def get_config_path(protocol_path, config_arg):
    """
    Get the configuration file path.

    :param protocol_path: Path to the protocol folder.
    :param config_arg: Command-line argument for the config file.
    :return: Path to the configuration file.
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

    :param protocol_name: Name of the protocol.
    :param config: Configuration data.
    """
    print("== Protocol name ==")
    print(protocol_name)
    print()
    print("== Selected configuration ==")
    for key, value in config.items():
        print(f"{key}\t\t\t{value}")
    print()


if __name__ == "__main__":
    args = parse_arguments()

    if not args.name:
        print("Error: missing protocol name")
        exit(1)

    protocol_path = get_protocol_path(args.name)
    config_path = get_config_path(protocol_path, args.config)

    config = utils.parse_config(config_path)
    config["iterations"] = args.iterations
    if utils.validate_config(config) is False:
        print("Invalid configuration")
        exit(1)
    config["name"] = args.name
    config["path"] = protocol_path
    config["verbose"] = args.verbose
    config["built"] = args.built
    config["max-top"] = args.max_top

    if args.verbose:
        display_verbose_info(args.name, config)

    result = utils.run_protocol(config)
    if result[0] is False:
        print(f"Error running protocol: {result[1]}")
        exit(1)
    utils.process_data(config)
