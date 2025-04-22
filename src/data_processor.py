#!/usr/bin/env python3
"""
data_processor.py

This module processes the results from the protocol execution. It is
responsible for reading the output files, parsing the data, and generating
reports.
"""

import os

import numpy as np


class DataProcessor:
    def __init__(self, config):
        """
        Initialize the DataProcessor with the configuration data.

        :param config: Configuration data for the protocol.
        """
        self._execfile = config.get("execfile")
        self._results = {}

    def process_nethogs(self):
        """
        Process the nethogs output file and populate the results.
        """
        output_file = os.path.join(os.path.dirname(
            __file__), "../results/nethogs_output.txt")
        if not os.path.exists(output_file):
            print("Error: nethogs_output.txt not found, "
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
                        if party_id not in self._results:
                            max_length = max(
                                (len(arr) for arr in self._results.values()),
                                default=0)
                            if max_length > 0:
                                self._results[party_id] = [0] * max_length
                            else:
                                self._results[party_id] = []
                        self._results[party_id].append(
                            float(data_amount)
                        )

        self._trim_arrays()

    def _trim_arrays(self):
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
        for data_amounts in self._results.values():
            start_idx, end_idx = find_trim_indices(data_amounts)
            global_start_idx = max(global_start_idx, start_idx)
            global_end_idx = min(global_end_idx, end_idx)

        self._results = {
            party_id: np.array(
                data_amounts[global_start_idx:global_end_idx + 2])
            for party_id, data_amounts in self._results.items()
        }
