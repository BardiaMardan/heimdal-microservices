"""Fleet telemetry: a moving vehicle reporting speed, fuel, and position."""
import random

from .base import Device


class FleetDevice(Device):
    device_type = "fleet"

    def reading(self) -> dict:
        return {
            "speed_kmh": round(random.uniform(0, 110), 1),
            "fuel_pct": round(random.uniform(5, 100), 1),
            "lat": round(random.uniform(51.0, 51.7), 5),
            "lon": round(random.uniform(-0.5, 0.3), 5),
        }
