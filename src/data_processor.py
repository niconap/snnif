#!/usr/bin/env python3
"""
data_processor.py

This module processes the results from the protocol execution. It is
responsible for reading the output files, parsing the data, and generating
reports.
"""

import os

import numpy as np
import matplotlib.pyplot as plt


class DataProcessor:
    def __init__(self, config):
        """
        Initialize the DataProcessor with the configuration data.

        :param config: Configuration data for the protocol.
        """
        self._execfile = config.get("execfile")
        self._iterations = config.get("iterations", 1)
        self._results = []

    def nethogs_graphs(self):
        """
        Generate graphs for the nethogs data.
        """
        self._parse_nethogs()
        averages = self._nethogs_averages()
        speeds = self._nethogs_speed()

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        os.makedirs(os.path.join(base_dir, "results"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "results/figures"), exist_ok=True)


        for party_id, data_amounts in averages.items():
            xs = np.arange(len(data_amounts)) * 0.5
            plt.plot(xs, data_amounts, label=f"Data Amounts - party {party_id}")
        plt.title("Data Amounts for All Parties")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Cumulative Data Amount (kB)")
        plt.legend()
        plt.savefig("results/figures/data_amounts.png")
        plt.clf()

        for party_id, speed in speeds.items():
            xs = np.arange(len(speed)) * 0.5
            plt.plot(xs, speed, label=f"Speed - party {party_id}")
        plt.title("Communication Speed for All Parties")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Speed (kB/s)")
        plt.legend()
        plt.savefig("results/figures/speed.png")
        plt.clf()

    def _parse_nethogs(self):
        """
        Parse and trim the nethogs output file and populate the results.
        """
        for i in range(self._iterations):
            self._results.append({})
            output_file = os.path.join(os.path.dirname(
                __file__), f"../results/nethogs_{i}.txt")
            if not os.path.exists(output_file):
                print(f"Error: nethogs_{i}.txt not found, "
                      "please run the protocol first")
                return

            with open(output_file, "r") as outfile:
                lines = outfile.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith(f"./{self._execfile}"):
                        parts = line.split()
                        path_parts = parts[0].split("/")
                        if len(path_parts) >= 3:
                            party_id = path_parts[-2]
                            data_amount = parts[1]
                            if party_id not in self._results[i]:
                                max_length = max(
                                    (len(arr)
                                     for arr in self._results[i].values()),
                                    default=0)
                                if max_length > 0:
                                    self._results[i][party_id] = [
                                        0] * max_length
                                else:
                                    self._results[i][party_id] = []
                            self._results[i][party_id].append(
                                float(data_amount)
                            )

            self._trim_arrays(i)

    def _nethogs_averages(self):
        """
        Calculate the point wise averages of the data amounts for each party
        across all iterations.
        """
        parties = self._results[0].keys()
        averages = {party_id: [] for party_id in parties}
        for i in range(self._iterations):
            for party_id in parties:
                if party_id in self._results[i]:
                    data_amounts = self._results[i][party_id]
                    if len(data_amounts) > 0:
                        averages[party_id].append(data_amounts)

        for party_id in parties:
            if averages[party_id]:
                averages[party_id] = np.mean(
                    np.array(averages[party_id]), axis=0
                )

        return averages

    def _nethogs_speed(self):
        """
        Calculate the speed of data transfer for each party across all
        iterations.
        """
        averages = self._nethogs_averages()
        speeds = {}
        for party_id, data_amounts in averages.items():
            speeds[party_id] = np.diff(data_amounts) / 0.5
            speeds[party_id] = np.insert(speeds[party_id], 0, 0)
        return speeds

    def _trim_arrays(self, iteration):
        """
        Trim leading and trailing repeated numbers from the arrays in _results
        based on the lowest start index and highest end index across all
        arrays.
        """
        def find_trim_indices(array):
            """
            Find the start and end indices for trimming an array.
            """
            start_idx = 0
            while (start_idx < len(array) - 1 and
                   array[start_idx] == array[start_idx + 1]):
                start_idx += 1

            end_idx = len(array) - 1
            while end_idx > 0 and array[end_idx] == array[end_idx - 1]:
                end_idx -= 1

            return start_idx, end_idx

        global_start_idx = 0
        global_end_idx = float('inf')
        for data_amounts in self._results[iteration].values():
            start_idx, end_idx = find_trim_indices(data_amounts)
            global_start_idx = max(global_start_idx, start_idx)
            global_end_idx = min(global_end_idx, end_idx)

        self._results[iteration] = {
            party_id: np.array(
                data_amounts[global_start_idx:global_end_idx + 2])
            for party_id, data_amounts in self._results[iteration].items()
        }