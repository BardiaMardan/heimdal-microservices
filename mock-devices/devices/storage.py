"""Storage / cold-chain unit: temperature, humidity, door state."""
import random

from .base import Device


class StorageDevice(Device):
    device_type = "storage"

    def reading(self) -> dict:
        return {
            "temperature_c": round(random.uniform(2, 8), 1),
            "humidity_pct": round(random.uniform(40, 70), 1),
            "door_open": random.random() < 0.05,
        }
