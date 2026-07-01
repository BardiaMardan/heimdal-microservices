"""Base mock device — the firmware every device type shares.

Lifecycle (one device, one thread):
  announce -> print 6-digit claim code -> poll until a human claims it in the UI
  -> fetch the operational token once -> stream telemetry forever.

Subclasses only implement reading(); the onboarding dance lives here.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone

from . import client


class Device:
    device_type = "generic"

    def __init__(self, name: str, location: str | None = None, interval: float = 3.0):
        self.name = name
        self.location = location
        self.interval = interval
        self.hardware_id = client.hardware_id_for(name)
        self.token: str | None = None
        self.mqtt = None

    # --- per-type telemetry; subclasses override ---
    def reading(self) -> dict:
        raise NotImplementedError

    # --- firmware ---
    def log(self, msg: str) -> None:
        with client.print_lock:
            print(f"  [{self.name}] {msg}")

    def run(self, stop: threading.Event, once: bool = False) -> None:
        if not self._provision(stop):
            return
        self.mqtt = client.connect_mqtt(self.hardware_id)
        self.log("provisioned — streaming telemetry over MQTT")
        try:
            while not stop.is_set():
                self._send(self.reading())
                if once:
                    break
                stop.wait(self.interval)
        finally:
            self._disconnect()

    def _provision(self, stop: threading.Event) -> bool:
        cached = client.load_state().get(self.hardware_id)
        if cached and cached.get("token"):
            self.token = cached["token"]
            self.log("already claimed (token cached) — streaming")
            return True

        # Reuse a prior secret if we announced but weren't claimed before; the
        # code itself is always fresh because the old one has likely expired.
        secret = (cached or {}).get("provisioning_secret") or client.gen_provisioning_secret()
        code = client.gen_claim_code()

        status, body = client.request(
            "POST",
            "/provisioning/announce",
            json_body={
                "hardware_id": self.hardware_id,
                "name": self.name,
                "type": self.device_type,
                "location": self.location,
                "code_hash": client.sha256_hex(code),
                "provisioning_secret_hash": client.sha256_hex(secret),
            },
        )
        if status != 200:
            self.log(f"announce failed ({status}): {body}")
            return False

        client.save_device_state(
            self.hardware_id,
            {"name": self.name, "provisioning_secret": secret, "token": None},
        )
        self._print_code(code)

        while not stop.is_set():
            status, body = client.request(
                "GET", f"/provisioning/status?hardware_id={self.hardware_id}"
            )
            if status == 200 and body["data"]["claimed"]:
                break
            stop.wait(2.0)
        if stop.is_set():
            return False

        self.log("claimed — fetching operational token")
        status, body = client.request(
            "POST",
            "/provisioning/token",
            json_body={"hardware_id": self.hardware_id, "provisioning_secret": secret},
        )
        token = (body.get("data") or {}).get("device_token") if status == 200 else None
        if not token:
            self.log(f"token fetch failed ({status}): {body}")
            return False

        self.token = token
        client.save_device_state(
            self.hardware_id,
            {"name": self.name, "provisioning_secret": secret, "token": token},
        )
        self.log("claimed — operational token acquired")
        return True

    def _print_code(self, code: str) -> None:
        with client.print_lock:
            print()
            print("  " + "=" * 52)
            print(f"   DEVICE: {self.name}  ({self.device_type})")
            print(f"   CLAIM CODE = {code}")
            print("   -> enter this in the dashboard within 10 minutes")
            print("  " + "=" * 52)
            print()

    def _send(self, reading: dict) -> None:
        payload = {"ts": datetime.now(timezone.utc).isoformat(), "readings": reading}
        self.mqtt.publish(
            client.telemetry_topic(self.hardware_id), json.dumps(payload), qos=1
        )
        self.log(json.dumps(reading))

    def _disconnect(self) -> None:
        if self.mqtt is None:
            return
        # Graceful shutdown: retract the retained 'online' with an explicit
        # 'offline' before dropping (the LWT only fires on ungraceful exits).
        self.mqtt.publish(
            client.status_topic(self.hardware_id),
            json.dumps({"state": "offline"}),
            qos=1,
            retain=True,
        )
        self.mqtt.loop_stop()
        self.mqtt.disconnect()
        self.mqtt = None
