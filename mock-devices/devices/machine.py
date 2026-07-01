"""Industrial machine: rotating equipment (lathe, CNC mill, pump)."""
import random

from .base import Device


class MachineDevice(Device):
    device_type = "machine"

    def reading(self) -> dict:
        return {
            "temperature_c": round(random.uniform(45, 85), 1),
            "vibration_mm_s": round(random.uniform(0.5, 6.0), 2),
            "rpm": random.randint(800, 3000),
        }
