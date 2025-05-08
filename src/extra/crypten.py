#!/usr/bin/env python3
"""
extra/falcon.py

This script is the extra data processor for the Falcon protocol.
"""

import matplotlib.pyplot as plt
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

    for file in config['extra_files']:
        file_path = os.path.join(results_dir, file)
        with open(file_path) as f:
            content = f.read()

        epoch_pattern = re.compile(
            r"Epoch: \[(\d+)\]\[(\d+)/\d+\].*?Loss ([\d.]+) \(([\d.]+)\).*?Prec@1 ([\d.]+) \(([\d.]+)\).*?Prec@5 ([\d.]+) \(([\d.]+)\)"
        )
        test_pattern = re.compile(
            r"Test: \[(\d+)/\d+\].*?Loss ([\d.]+) \(([\d.]+)\).*?Prec@1 ([\d.]+) \(([\d.]+)\).*?Prec@5 ([\d.]+) \(([\d.]+)\)"
        )

        # Extract matches
        epochs = []
        tests = []

        for match in epoch_pattern.finditer(content):
            epoch_data = {
                "epoch": int(match.group(1)),
                "batch": int(match.group(2)),
                "loss": float(match.group(3)),
                "avg_loss": float(match.group(4)),
                "prec1": float(match.group(5)),
                "avg_prec1": float(match.group(6)),
                "prec5": float(match.group(7)),
                "avg_prec5": float(match.group(8)),
            }
            epochs.append(epoch_data)

        for match in test_pattern.finditer(content):
            test_data = {
                "batch": int(match.group(1)),
                "loss": float(match.group(2)),
                "avg_loss": float(match.group(3)),
                "prec1": float(match.group(4)),
                "avg_prec1": float(match.group(5)),
                "prec5": float(match.group(6)),
                "avg_prec5": float(match.group(7)),
            }
            tests.append(test_data)

    return {"epoch": epochs, "test": tests}


def process_data(data):
    """
    Create plots specifically for the Crypten protocol, these will be stored in
    the results directory.

    :param data: The data parsed by the retrieve_data function
    """
    epoch_data = data["epoch"]
    test_data = data["test"]

    epochs = {}
    for entry in epoch_data:
        epoch_num = entry["epoch"]
        if epoch_num not in epochs:
            epochs[epoch_num] = {"batches": [], "prec1": []}
        epochs[epoch_num]["batches"].append(entry["batch"])
        epochs[epoch_num]["prec1"].append(entry["prec1"])

    test_batches = [entry["batch"] for entry in test_data]
    test_prec1 = [entry["avg_prec1"] for entry in test_data]

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for epoch_num, values in epochs.items():
        ax1.scatter(
            values["batches"], values["prec1"],
            label=f"Epoch {epoch_num}", alpha=0.7
        )

    ax1.set_title("Training Prec@1 by Batch and Epoch")
    ax1.set_xlabel("Batch")
    ax1.set_ylabel("Prec@1 (%)")
    ax1.legend()
    ax1.grid(True)

    tests_per_epoch = 4
    num_epochs = len(test_data) // tests_per_epoch
    colors = plt.get_cmap("tab10", num_epochs)

    for i in range(num_epochs):
        start = i * tests_per_epoch
        end = start + tests_per_epoch
        batch_segment = test_batches[start:end]
        prec_segment = test_prec1[start:end]
        ax2.scatter(
            batch_segment, prec_segment,
            color=colors(i), label=f"Epoch {i}"
        )

    ax2.set_title("Test Prec@1 by Batch and Epoch")
    ax2.set_xlabel("Batch")
    ax2.set_ylabel("Avg Prec@1 (%)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(
        os.path.join(os.getcwd(), "results", "crypten_training.png"),
        dpi=300
    )
