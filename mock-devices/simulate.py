#!/usr/bin/env python3
"""Mock IIoT devices ("ESPs") for Heimdall.

Standard-library only — no pip install needed.

What it does today:
  1. Authenticates against the backend REST API (registers a dev user, logs in).
  2. Ensures every device in devices.json exists in the device registry
     (idempotent: matches existing devices by name).
  3. Simulates each device emitting realistic telemetry on an interval.

NOTE: the telemetry transport does not exist yet. Until the MQTT ingestion path
is built (next increments), `send_telemetry()` just prints the reading. The seam
is deliberate: swap that one function for an MQTT publish and these become real
publishers. See docs/adr/0002-mqtt-ingestion.md.

Usage:
  python3 simulate.py                 # register devices + stream readings
  python3 simulate.py --once          # one reading per device, then exit
  python3 simulate.py --register-only # just ensure devices exist
  HEIMDALL_API=http://localhost:8000/api/v1 \
  HEIMDALL_EMAIL=op@factory.io HEIMDALL_PASSWORD=pw12345 python3 simulate.py
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = os.environ.get("HEIMDALL_API", "http://localhost:8000/api/v1")
EMAIL = os.environ.get("HEIMDALL_EMAIL", "op@factory.io")
PASSWORD = os.environ.get("HEIMDALL_PASSWORD", "pw12345")
INTERVAL_S = float(os.environ.get("HEIMDALL_INTERVAL", "3"))
DEVICES_FILE = Path(__file__).parent / "devices.json"


def _request(method: str, path: str, *, token: str | None = None, json_body=None, form=None):
    url = f"{API}{path}"
    headers = {}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")
    except urllib.error.URLError as e:
        print(f"  ! cannot reach {API} — is the backend running? ({e.reason})")
        sys.exit(1)


def authenticate() -> str:
    _request("POST", "/auth/register", json_body={"email": EMAIL, "password": PASSWORD})
    status, body = _request(
        "POST", "/auth/login/access-token", form={"username": EMAIL, "password": PASSWORD}
    )
    if status != 200:
        print(f"  ! login failed ({status}): {body}")
        sys.exit(1)
    print(f"  authenticated as {EMAIL}")
    return body["data"]["access_token"]


def ensure_devices(token: str) -> dict[str, str]:
    """Return {device_name: device_id}, creating any that don't exist yet."""
    _, body = _request("GET", "/devices?limit=500", token=token)
    existing = {d["name"]: d["id"] for d in (body.get("data") or [])}
    wanted = json.loads(DEVICES_FILE.read_text())
    ids: dict[str, str] = {}
    for d in wanted:
        if d["name"] in existing:
            ids[d["name"]] = existing[d["name"]]
            print(f"  = {d['name']} (exists)")
            continue
        status, created = _request("POST", "/devices", token=token, json_body=d)
        if status == 201:
            ids[d["name"]] = created["data"]["id"]
            print(f"  + {d['name']} ({d['type']}) -> {created['data']['id']}")
        else:
            print(f"  ! failed to create {d['name']} ({status}): {created}")
    return ids


def reading_for(device_type: str) -> dict:
    """A plausible telemetry payload per device domain (random-walk-ish)."""
    if device_type == "machine":
        return {
            "temperature_c": round(random.uniform(45, 85), 1),
            "vibration_mm_s": round(random.uniform(0.5, 6.0), 2),
            "rpm": random.randint(800, 3000),
        }
    if device_type == "environmental":
        return {
            "temperature_c": round(random.uniform(-5, 30), 1),
            "humidity_pct": round(random.uniform(20, 90), 1),
            "co2_ppm": random.randint(400, 1200),
        }
    if device_type == "fleet":
        return {
            "speed_kmh": round(random.uniform(0, 110), 1),
            "fuel_pct": round(random.uniform(5, 100), 1),
            "lat": round(random.uniform(51.0, 51.7), 5),
            "lon": round(random.uniform(-0.5, 0.3), 5),
        }
    if device_type == "storage":
        return {
            "temperature_c": round(random.uniform(2, 8), 1),
            "humidity_pct": round(random.uniform(40, 70), 1),
            "door_open": random.random() < 0.05,
        }
    return {"value": round(random.random(), 4)}


def send_telemetry(device_id: str, device_type: str, reading: dict) -> None:
    # TODO(ingestion): publish to MQTT topic heimdall/<device_id>/telemetry (QoS 1)
    # once the ingestion service exists. For now we just print.
    print(f"  -> {device_id[:8]} [{device_type:13}] {json.dumps(reading)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Mock Heimdall IIoT devices.")
    ap.add_argument("--once", action="store_true", help="emit one reading per device, then exit")
    ap.add_argument("--register-only", action="store_true", help="only ensure devices exist")
    args = ap.parse_args()

    print(f"Heimdall mock devices -> {API}")
    token = authenticate()
    type_by_name = {d["name"]: d["type"] for d in json.loads(DEVICES_FILE.read_text())}
    ids = ensure_devices(token)
    if args.register_only:
        return

    print(f"\nStreaming telemetry every {INTERVAL_S}s (Ctrl-C to stop)\n")
    try:
        while True:
            for name, device_id in ids.items():
                dtype = type_by_name[name]
                send_telemetry(device_id, dtype, reading_for(dtype))
            if args.once:
                break
            time.sleep(INTERVAL_S)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
