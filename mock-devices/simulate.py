#!/usr/bin/env python3
"""Run the mock Heimdall IIoT fleet.

Each device in devices.json boots, announces itself to the backend's
provisioning plane, and prints a 6-digit CLAIM CODE. Enter that code in the
dashboard ("Connect a device") to claim it to your account; the device then
fetches its operational token and starts streaming telemetry.

Devices are clients, not servers — they dial out to the backend, so their IP is
irrelevant and there is nothing to "scan". See ../docs/notes/Note07-*.

Standard-library only; nothing to install.

Usage:
  python3 simulate.py            # boot the whole fleet, wait to be claimed, stream
  python3 simulate.py --once     # one telemetry reading per device after claiming
  python3 simulate.py --reset    # forget claimed state and re-onboard from scratch

Env (defaults): HEIMDALL_API=http://localhost:8000/api/v1  HEIMDALL_INTERVAL=3
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
from pathlib import Path

from devices import build, client

DEVICES_FILE = Path(__file__).parent / "devices.json"
INTERVAL_S = float(os.environ.get("HEIMDALL_INTERVAL", "3"))


def main() -> None:
    ap = argparse.ArgumentParser(description="Mock Heimdall IIoT fleet.")
    ap.add_argument("--once", action="store_true", help="one reading per device after claim, then exit")
    ap.add_argument("--reset", action="store_true", help="clear saved claim state and re-onboard")
    args = ap.parse_args()

    if args.reset:
        client.clear_state()
        print("device state cleared — every device will re-onboard.")

    specs = json.loads(DEVICES_FILE.read_text())
    fleet = [build(spec, interval=INTERVAL_S) for spec in specs]

    print(f"Heimdall mock fleet -> {client.API}  ({len(fleet)} devices)")
    print("Unclaimed devices will print a CLAIM CODE below. Ctrl-C to stop.\n")

    stop = threading.Event()
    threads = [
        threading.Thread(target=d.run, args=(stop,), kwargs={"once": args.once}, daemon=True)
        for d in fleet
    ]
    for t in threads:
        t.start()

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nstopping...")
        stop.set()
    for t in threads:
        t.join(timeout=3)


if __name__ == "__main__":
    main()
