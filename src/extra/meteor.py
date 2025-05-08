#!/usr/bin/env python3
"""
extra/meteor.py

This script is the extra data processor for the Meteor protocol.
"""

import os
import re


def retrieve_data(docker_manager, config):
    """
    Retrieve the extra data from the docker container and store it into a
    dictionary.

    :param docker_manager: The docker manager managing the active container
    :returns: The data parsed into a dictionary
    """
    results_dir = os.path.join(os.getcwd(), "results")
    for file in config['extra_files']:
        local_file = os.path.join(results_dir, file)
        docker_manager.retrieve_file(
            f'{docker_manager.workdir}/{file}', local_file)

    parsed_data = {}

    for file in config['extra_files']:
        file_path = os.path.join(results_dir, file)
        with open(file_path) as f:
            content = f.read()

        wall_clock_pattern = (
            r"Wall Clock time for .*?: ([\d.]+) sec"
        )
        cpu_time_pattern = r"CPU time for .*?: ([\d.]+) sec"
        total_comm_pattern = (
            r"Total communication: ([\d.]+)MB \(sent\) and ([\d.]+)MB \(recv\)"
        )
        total_calls_pattern = (
            r"Total calls: (\d+) \(sends\) and (\d+) \(recvs\)"
        )
        party_comm_pattern = (
            r"Communication, .*?, (P\d+): ([\d.]+)MB \(sent\) "
            r"([\d.]+)MB \(recv\)"
        )
        party_rounds_pattern = (
            r"Rounds, .*?, (P\d+): (\d+)\(sends\) (\d+)\(recvs\)"
        )

        wall_clock_times = re.findall(wall_clock_pattern, content)
        cpu_times = re.findall(cpu_time_pattern, content)
        total_comms = re.findall(total_comm_pattern, content)
        total_calls = re.findall(total_calls_pattern, content)
        party_comms = re.findall(party_comm_pattern, content)
        party_rounds = re.findall(party_rounds_pattern, content)

        wall_clock_times = [float(x) for x in wall_clock_times]
        cpu_times = [float(x) for x in cpu_times]
        total_comms = [(float(x[0]), float(x[1])) for x in total_comms]
        total_calls = [(int(x[0]), int(x[1])) for x in total_calls]
        party_comms = [(x[0], float(x[1]), float(x[2])) for x in party_comms]
        party_rounds = [(x[0], int(x[1]), int(x[2])) for x in party_rounds]

        parsed_data[file] = {
            'wall_clock_times': wall_clock_times,
            'cpu_times': cpu_times,
            'total_comms': total_comms,
            'total_calls': total_calls,
            'party_comms': party_comms,
            'party_rounds': party_rounds
        }

    return parsed_data


def process_data(data):
    """
    Create plots specifically for the Meteor protocol, these will be stored in
    the results directory.

    :param data: The data parsed by the retrieve_data function
    """
    if 'Meteor_P0.txt' in data:
        values = data['Meteor_P0.txt']
        print("Overall Metrics (from Meteor_P0.txt):")
        print(f"Total Communications: {values['total_comms']}")
        print(f"Total Calls: {values['total_calls']}")
        print("\n")

    for file, values in data.items():
        print(f"File: {file}")
        print(f"Wall Clock Times: {values['wall_clock_times']}")
        print(f"CPU Times: {values['cpu_times']}")
        print(f"Party Communications: {values['party_comms']}")
        print(f"Party Rounds: {values['party_rounds']}")
        print("\n")
