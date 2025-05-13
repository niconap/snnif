import getpass
import importlib
import json
import os
import time
import shutil
import subprocess

import psutil
from docker_manager import DockerManager
from data_processor import DataProcessor


def parse_config(config_path):
    """
    Parse the configuration file. In case of an invalid configuration, exit the
    program with an error message.

    :param config_path: Path to the configuration file.
    :return: Parsed configuration data.
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
    Validate the configuration data. In case of an invalid configuration,
    return false.

    :param config: Parsed configuration data.
    """
    required_keys = ["run", "image", "execfile"]
    for key in required_keys:
        if key not in config or config[key] == '':
            print(f"Missing required key '{key}' in configuration.")
            return False
    if "extra" not in config:
        config["extra"] = False
    if "iterations" not in config:
        config["iterations"] = 1
    if config["iterations"] < 1:
        print("Error: The number of iterations must be at least 1.")
        return False


def run_protocol(config, sudo_password=None):
    """
    Run the protocol using Docker.

    :param config: Configuration data.
    :param sudo_password: Sudo password for Scaphandre, if required.
    :return: Tuple indicating success and a message.
    """
    scaphandre_installed = True
    scaphandre_path = shutil.which("scaphandre")

    if scaphandre_path is None:
        scaphandre_installed = False
        print("Scaphandre is not installed or not in PATH, skipping power"
              " measurements")

    docker_manager = DockerManager(config)
    docker_manager.build_image()
    docker_manager.run_container()

    if scaphandre_installed:
        if sudo_password is None:
            prompt_message = "Enter your sudo password (for Scaphandre): "
            sudo_password = getpass.getpass(prompt=prompt_message)

        sudo_validation_proc = subprocess.Popen(
            ["sudo", "-S", "echo"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        sudo_validation_proc.stdin.write(f"{sudo_password}\n".encode())
        sudo_validation_proc.stdin.flush()
        sudo_validation_proc.stdin.close()
        sudo_validation_proc.wait()

        if sudo_validation_proc.returncode != 0:
            return False, "Incorrect sudo password"

    try:
        docker_manager.copy_file(
            os.path.join(os.path.dirname(__file__), "protocol_manager.py"),
            docker_manager.workdir
        )
        command = (
            f'python3 protocol_manager.py --command "{config["run"]}" '
            f'--iterations {config["iterations"]}'
        )
        if config["verbose"]:
            command += " --verbose"

        if scaphandre_installed:
            # The file is created first, otherwise Scaphandre will not be able
            # to write to it. This also ensures the file is flushed.
            if not os.path.exists("results"):
                os.makedirs("results")

            with open("results/scaphandre.json", "w") as f:
                f.write("")

            if config['max-top'] == 0:
                process_amt = len(psutil.pids())
                if config["verbose"]:
                    print(f"Found {process_amt} processes, setting --max-top "
                          f"to {process_amt + 10} to avoid missing any process"
                          )
                config["max-top"] = process_amt + 10

            print(f"Max top consumers set to {config['max-top']}")
            scaphandre_proc = subprocess.Popen(
                ["sudo", "-S", "scaphandre", "json", "-s", "0", "--step-nano",
                 "10000", "--containers", "--max-top-consumers",
                 str(config["max-top"]), "-f", "results/scaphandre.json",],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )

            scaphandre_proc.stdin.write(f"{sudo_password}\n".encode())
            scaphandre_proc.stdin.flush()
            sudo_password = None

        print("Starting protocol execution...")

        time1 = docker_manager.run_command("date +%s%3N")
        docker_manager.run_command(command)
        time2 = docker_manager.run_command("date +%s%3N")

        time.sleep(1)
        if scaphandre_installed:
            scaphandre_proc.terminate()
            scaphandre_proc.wait()

        results_dir = os.path.join(os.getcwd(), "results")
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        for run in range(config["iterations"]):
            remote_file = f"{docker_manager.workdir}/nethogs_{run}.txt"
            local_file = os.path.join(results_dir, f"nethogs_{run}.txt")
            docker_manager.retrieve_file(remote_file, local_file)
        docker_manager.retrieve_file(
            f"{docker_manager.workdir}/time.txt", os.path.join(results_dir,
                                                               "time.txt"))
        print((int(time2) - int(time1)) / 1000.0, "second(s) elapsed in total")
        handle_extra(docker_manager, config)
    except KeyboardInterrupt:
        print("Program interrupted, deleting the Docker container...")
    finally:
        docker_manager.stop_container()
    return True, "Protocol executed successfully"


def handle_extra(docker_manager, config):
    """
    Handle the extra data processing.

    :param config: Configuration data.
    """
    if not config['extra']:
        return

    extra = importlib.import_module(f"extra.{config['name']}")
    if not hasattr(extra, "retrieve_data"):
        print(f"Error: extra module '{config['name']}' does not have "
              "'retrieve_data' function")
        exit(1)
    if not hasattr(extra, "process_data"):
        print(f"Error: extra module '{config['name']}' does not have "
              "'process_data' function")
        exit(1)

    data = extra.retrieve_data(docker_manager, config)
    extra.process_data(data)


def process_data(config):
    """
    Process the data after running the protocol.

    :param config: Configuration data.
    """
    processor = DataProcessor(config)
    processor.nethogs_graphs()
    processor.scaphandre_graphs()
