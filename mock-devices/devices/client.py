"""Shared 'firmware' plumbing for the mock Heimdall fleet.

Standard library only. Handles: HTTP to the backend provisioning plane, the
hashing a real device would do locally, deterministic hardware ids, and a small
on-disk state file so reruns remember what's already been claimed.

A real device would burn its hardware id + keys in at manufacture. Here we fake
the identity with a uuid5 of the name. Provisioning (bootstrap) talks REST over
stdlib urllib; telemetry (the hot path) talks MQTT via paho — exactly the
control-plane/data-plane split real firmware uses. See ../README.md and
../../docs/adr/0002-mqtt-ingestion.md.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import threading
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

API = os.environ.get("HEIMDALL_API", "http://localhost:8000/api/v1")
MQTT_HOST = os.environ.get("HEIMDALL_MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("HEIMDALL_MQTT_PORT", "1883"))
TOPIC_PREFIX = os.environ.get("HEIMDALL_MQTT_PREFIX", "heimdall")
STATE_FILE = Path(__file__).resolve().parent.parent / ".device_state.json"

_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "heimdall-mock-devices")
_state_lock = threading.Lock()
print_lock = threading.Lock()


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def gen_claim_code() -> str:
    """A 6-digit, zero-padded claim code. secrets, not random — it's a secret."""
    return f"{secrets.randbelow(1_000_000):06d}"


def gen_provisioning_secret() -> str:
    return secrets.token_urlsafe(24)


def hardware_id_for(name: str) -> str:
    """Stable per name, so reruns reuse the same device row instead of orphaning it."""
    return f"hw-{uuid.uuid5(_NAMESPACE, name)}"


def request(method: str, path: str, *, json_body=None):
    url = f"{API}{path}"
    headers = {}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or "null")
    except urllib.error.URLError as e:
        print(f"  ! cannot reach {API} — is the backend running? ({e.reason})")
        sys.exit(1)


def telemetry_topic(hardware_id: str) -> str:
    return f"{TOPIC_PREFIX}/{hardware_id}/telemetry"


def status_topic(hardware_id: str) -> str:
    return f"{TOPIC_PREFIX}/{hardware_id}/status"


def connect_mqtt(hardware_id: str) -> "mqtt.Client":
    """Connect a device's MQTT client. The Last Will (retained 'offline' on the
    status topic) is what lets the backend notice an ungraceful disconnect; we
    publish a retained 'online' on connect to clear it. QoS/prefix mirror the
    backend subscriber."""
    client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=hardware_id)
    status = status_topic(hardware_id)
    client.will_set(status, json.dumps({"state": "offline"}), qos=1, retain=True)
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()
    client.publish(status, json.dumps({"state": "online"}), qos=1, retain=True)
    return client


def load_state() -> dict:
    with _state_lock:
        return _read_unlocked()


def save_device_state(hardware_id: str, record: dict) -> None:
    with _state_lock:
        state = _read_unlocked()
        state[hardware_id] = record
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        os.replace(tmp, STATE_FILE)  # atomic on POSIX


def clear_state() -> None:
    with _state_lock:
        if STATE_FILE.exists():
            STATE_FILE.unlink()


def _read_unlocked() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return {}
