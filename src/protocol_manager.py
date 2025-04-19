#!/usr/bin/env python3
"""
protocol_manager.py

This module manages protocols inside the Docker container. The manager is
responsible for running the protocol and for taking measurements.
"""

import argparse
import sys
import time

from scapy.sendrecv import AsyncSniffer
import subprocess
from scapy.layers.inet import IP

if __name__ == "__main__":
    def main():
        parser = argparse.ArgumentParser(description="Protocol Manager")
        parser.add_argument("--command", type=str,
                            required=True, help="Command to run")
        parser.add_argument("--verbose", action="store_true")
        args = parser.parse_args()

        print("Starting sniffing...")
        sniffer = AsyncSniffer(iface="lo", store=True)
        sniffer.start()
        start_time = time.time()

        result = subprocess.run(args.command, shell=True)
        if result.stderr:
            print(f"Command error:\n{result.stderr}", file=sys.stderr)

        stop_time = time.time()

        # Wait for a few seconds to ensure all packets are captured
        time.sleep(3)
        sniffer.stop()
        packets = sniffer.results
        print(f"Running took {stop_time - start_time:.2f} seconds")

        total_size = 0
        for packet in packets:
            packet_size = len(packet)
            total_size += packet_size
            if args.verbose:
                if IP in packet:
                    print(
                        f"Packet: {packet[IP].summary()}, Size: {packet_size} bytes")
                else:
                    print(f"Unknown packet type, Size: {packet_size} bytes")

        print(f"Total size of captured packets: {total_size} bytes")
        print(f"Total number of packets: {len(packets)}")

    try:
        main()
    except KeyboardInterrupt:
        print("\nProtocol Manager interrupted", file=sys.stderr)
        sys.exit(1)
