#!/usr/bin/env python3
"""
Run the host's fabricPattern.sh from inside the container.

Usage (inside the container):
    python run_fabric_pattern.py zigzag

Environment variables you can override:
    HOST_USER          – default: ssbrpi
    HOST_IP            – default: 172.17.0.1          (bridge IP you found)
    REMOTE_SCRIPT      – default: /home/ssbrpi/Project/Fabric/fabricPattern.sh
    SSH_IDENTITY_FILE  – path to a private key (if you use key auth)
"""

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

HOST_USER = os.getenv("HOST_USER", "ssbrpi")
HOST_IP = os.getenv("HOST_IP", "172.17.0.1")           # bridge IP or host.docker.internal
REMOTE_SCRIPT = os.getenv(
    "REMOTE_SCRIPT",
    "/home/ssbrpi/Project/Fabric/fabric",
)
SSH_IDENTITY_FILE = os.getenv("SSH_IDENTITY_FILE")      # optional

def run_fabric_pattern(pattern_name: str) -> str:
    """
    Execute `/home/ssbrpi/Project/Fabric/fabricPattern.sh <pattern_name>` on the host
    via SSH and return its stdout.

    Raises
    ------
    subprocess.CalledProcessError
        if the remote command returns a non‑zero exit status.
    """
    if not pattern_name:
        raise ValueError("pattern_name must be non‑empty")

    # Compose remote command safely.
    remote_cmd = f"{shlex.quote(REMOTE_SCRIPT)} {shlex.quote(pattern_name)}"

    # Build SSH invocation.
    ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",               # fail fast if auth fails
        "-o", "StrictHostKeyChecking=no",    # skip host‑key prompt (optional)
    ]
    if SSH_IDENTITY_FILE:
        ssh_cmd += ["-i", SSH_IDENTITY_FILE]

    ssh_cmd.append(f"{HOST_USER}@{HOST_IP}")
    ssh_cmd.append(remote_cmd)

    print(f"ssh cmd: {ssh_cmd}")
    print(f"ssh cmd: {' '.join(ssh_cmd)}", file=sys.stderr)

    completed = subprocess.run(
        ssh_cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,        # raises CalledProcessError on non‑zero exit
    )
    return completed.stdout

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the host's fabricPattern.sh via SSH"
    )
    parser.add_argument(
        "pattern",
        help="Pattern name passed to fabricPattern.sh (e.g. zigzag, 'hii there')",
    )
    args = parser.parse_args()

    try:
        output = run_fabric_pattern(args.pattern)
        print(output, end="")
    except subprocess.CalledProcessError as err:
        # Preserve remote stderr for easier debugging.
        print(err.stderr, file=sys.stderr, end="")
        sys.exit(err.returncode)

if __name__ == "__main__":
    main()
