"""Environmental sensor: ambient temperature, humidity, air quality."""
import random

from .base import Device


class EnvironmentalDevice(Device):
    device_type = "environmental"

    def reading(self) -> dict:
        return {
            "temperature_c": round(random.uniform(-5, 30), 1),
            "humidity_pct": round(random.uniform(20, 90), 1),
            "co2_ppm": random.randint(400, 1200),
        }
