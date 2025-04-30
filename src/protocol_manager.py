#!/usr/bin/env python3
"""
protocol_manager.py

This module manages protocols inside the Docker container. The manager is
responsible for running the protocol and for taking measurements.
"""

import argparse
import subprocess
import time
import os
import signal
import sys

if __name__ == "__main__":
    def main():
        parser = argparse.ArgumentParser(description="Protocol Manager")
        parser.add_argument("--command", type=str,
                            required=True, help="Command to run")
        parser.add_argument("--iterations", type=int, default=1,
                            help="Number of iterations to run (minimum 1)")
        parser.add_argument("--verbose", action="store_true")
        args = parser.parse_args()

        if args.iterations < 1:
            print("Error: The number of iterations must be at least 1.")
            sys.exit(1)

        nethogs_cmd = ["nethogs", "lo", "-a", "-t", "-d", "0", "-v", "1"]

        for run in range(args.iterations):
            output_file = f"nethogs_{run}.txt"

            with open(output_file, "w") as outfile:
                nethogs_proc = subprocess.Popen(
                    nethogs_cmd,
                    stdout=outfile,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
                start_time = time.time()

                result = subprocess.run(args.command, shell=True)
                if result.stderr:
                    print(f"Command error:\n{result.stderr}", file=sys.stderr)

                stop_time = time.time()

                # Ensure that all traffic is captured by waiting for a second
                time.sleep(1)

                os.killpg(os.getpgid(nethogs_proc.pid), signal.SIGTERM)
                nethogs_stop_time = time.time()
                with open('time.txt', 'a') as time_file:
                    duration = nethogs_stop_time - start_time
                    time_file.write(f"nethogs_{run}: {duration}\n")
                    iteration_duration = stop_time - start_time
                    time_file.write(f"iteration_{run}: {iteration_duration}\n")
    try:
        main()
    except KeyboardInterrupt:
        print("\nProtocol Manager interrupted", file=sys.stderr)
        sys.exit(1)
