"""Mock Heimdall IIoT device fleet — one class per target domain.

Each device is a small standalone 'firmware' that onboards via the backend
provisioning plane (announce -> claim code -> token) and then streams telemetry.
"""
from . import client
from .base import Device
from .environmental import EnvironmentalDevice
from .fleet import FleetDevice
from .machine import MachineDevice
from .storage import StorageDevice

REGISTRY: dict[str, type[Device]] = {
    "machine": MachineDevice,
    "environmental": EnvironmentalDevice,
    "fleet": FleetDevice,
    "storage": StorageDevice,
}


def build(spec: dict, interval: float = 3.0) -> Device:
    """Construct the right Device subclass from a devices.json entry."""
    try:
        cls = REGISTRY[spec["type"]]
    except KeyError:
        raise ValueError(
            f"unknown device type {spec.get('type')!r}; "
            f"expected one of {sorted(REGISTRY)}"
        )
    return cls(name=spec["name"], location=spec.get("location"), interval=interval)


__all__ = [
    "client",
    "build",
    "REGISTRY",
    "Device",
    "MachineDevice",
    "EnvironmentalDevice",
    "FleetDevice",
    "StorageDevice",
]
