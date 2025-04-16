import argparse
import os
import json


def parse_config(config_path):
    """
    Parse the configuration file. In case of an invalid configuration, exit the
    program with an error message.

    @param config_path: Path to the configuration file.
    @return: Parsed configuration data (dictionary).
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

    @param config: Parsed configuration data (dictionary).
    """
    required_keys = ["run", "args", "image"]
    for key in required_keys:
        if key not in config or not config[key]:
            print(f"Missing required key '{key}' in configuration.")
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Name of the protocol")
    parser.add_argument("--name", "-n", type=str, help="Protocol name")
    parser.add_argument("--config", "-c", type=str,
                        help="Path to the configuration file")
    args = parser.parse_args()

    if not args.name:
        print("Missing protocol name")
        exit(1)

    print(f"Protocol name: {args.name}")

    protocol_path = os.path.join(os.getcwd(), "protocols", args.name)
    if not os.path.exists(protocol_path):
        print(f"Protocol folder '{protocol_path}' does not exist")
        exit(1)

    if args.config:
        config_path = os.path.abspath(args.config)
    else:
        config_path = os.path.join(protocol_path, "config.json")
    if not os.path.exists(config_path):
        print(f"Protocol config file '{config_path}' does not exist")
        exit(1)

    config = parse_config(config_path)
    validate_config(config)
