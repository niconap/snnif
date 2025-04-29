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
from scipy.interpolate import interp1d


class DataProcessor:
    def __init__(self, config):
        """
        Initialize the DataProcessor with the configuration data.

        :param config: Configuration data for the protocol.
        """
        self._execfile = config.get("execfile")
        self._iterations = config.get("iterations", 1)
        self._avg_delays = []
        self._results = []
        self._averages = None
        self._target_delay = config.get("target_delay", 0.01)

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
            xs = np.arange(len(data_amounts)) * self._target_delay
            plt.plot(xs, data_amounts, label=f"Data Amounts - party {party_id}")
        plt.title("Data Amounts for All Parties")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Cumulative Data Amount (kB)")
        plt.legend()
        plt.savefig("results/figures/data_amounts.png")
        plt.clf()

        for party_id, speed in speeds.items():
            xs = np.arange(len(speed)) * self._target_delay
            plt.plot(xs, speed, label=f"Speed - party {party_id}")
        plt.title("Communication Speed for All Parties")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Speed (kB/s)")
        plt.legend()
        plt.savefig("results/figures/speed.png")
        plt.clf()

    def _calculate_iteration_time(self, iteration_index, measurement_amt):
        """
        Calculate the average delay for a specific iteration by reading the time
        from the results/time.txt file.

        :param iteration_index: The index of the current iteration.
        :param measurement_amt: The number of measurements in the iteration.
        :return: The average delay for the iteration.
        """
        time_file = os.path.join(os.path.dirname(__file__), "../results/time.txt")
        if not os.path.exists(time_file):
            print(f"Error: time.txt not found, please run the protocol first")
            return None

        with open(time_file, "r") as time_file:
            lines = time_file.readlines()
            for line in lines:
                if line.startswith(f"nethogs_{iteration_index}:"):
                    parts = line.split(":")
                    iteration_time = float(parts[1].strip())
                    break
            else:
                print(f"Error: iteration_{iteration_index} not found in time.txt")
                return None

        return iteration_time / measurement_amt if measurement_amt > 0 else 0

    def _parse_nethogs(self):
        """
        Parse and trim the nethogs output file and populate the results. The
        results get stored in the following format in self._results:
        [
            {
                "party_id": [data_amounts],
                ...
            },
            ...
        ]
        where each dictionary corresponds to an iteration.
        """
        for i in range(self._iterations):
            self._results.append({})
            output_file = os.path.join(os.path.dirname(
                __file__), f"../results/nethogs_{i}.txt")
            if not os.path.exists(output_file):
                print(f"Error: nethogs_{i}.txt not found, "
                      "please run the protocol first")
                return

            measurement_amt = 0
            with open(output_file, "r") as outfile:
                lines = outfile.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("Refreshing"):
                        measurement_amt += 1
                    if line.startswith(f"./{self._execfile}") or line.startswith(f"/{self._execfile}"):
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

            party_ids = sorted(self._results[i].keys())
            for j, party_id in enumerate(party_ids):
                self._results[i][j] = self._results[i].pop(party_id)

            avg_delay = self._calculate_iteration_time(i, measurement_amt)
            if avg_delay is not None:
                self._avg_delays.append(avg_delay)

    def _nethogs_averages(self):
        """
        Calculate the point wise averages of the data amounts for each party
        across all iterations.
        """
        if self._averages is not None:
            return self._averages

        time_file = os.path.join(os.path.dirname(__file__), "../results/time.txt")
        if not os.path.exists(time_file):
            print(f"Error: time.txt not found, please run the protocol first")
            return None

        with open(time_file, "r") as time_file:
            lines = time_file.readlines()
            max_time = 0
            for line in lines:
                if line.startswith("iteration_"):
                    parts = line.split(":")
                    iteration_time = float(parts[1].strip())
                    max_time = max(max_time, iteration_time)

        target_timestamps = np.arange(0, max_time, self._target_delay)
        interpolated_results = {}
        for i in range(self._iterations):
            for party_id, data_amounts in self._results[i].items():
                if party_id not in interpolated_results:
                    interpolated_results[party_id] = []
                orig_times = np.arange(len(data_amounts)) * self._avg_delays[i]
                interp_func = interp1d(orig_times, data_amounts,
                                       kind='nearest', bounds_error=False,
                                       fill_value="extrapolate")
                resampled = interp_func(target_timestamps)
                interpolated_results[party_id].append(resampled)

        averages = {}
        for party_id, resampled_array in interpolated_results.items():
            averages[party_id] = np.mean(resampled_array, axis=0)

        self._averages = averages
        return averages

    def _nethogs_speed(self):
        """
        Calculate the speed of data transfer for each party across all
        iterations.
        """
        averages = self._nethogs_averages()
        speeds = {}
        for party_id, data_amounts in averages.items():
            delay = self._target_delay
            speed = np.zeros(len(data_amounts))
            for i in range(1, len(data_amounts)):
                speed[i] = (data_amounts[i] - data_amounts[i - 1]) / delay
            speeds[party_id] = speed
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