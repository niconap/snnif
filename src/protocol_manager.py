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
        parser.add_argument("--verbose", action="store_true")
        args = parser.parse_args()

        output_file = "nethogs_output.txt"
        nethogs_cmd = ["nethogs", "lo", "-a", "-t", "-d", "0.5", "-v", "1"]

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

        print(f"Running took {stop_time - start_time:.2f} seconds")

        if args.verbose:
            print("Last 10 lines of nethogs output:")
            with open(output_file, "r") as outfile:
                lines = outfile.readlines()
                for line in lines[-10:]:
                    print(line.strip())

    try:
        main()
    except KeyboardInterrupt:
        print("\nProtocol Manager interrupted", file=sys.stderr)
        sys.exit(1)
