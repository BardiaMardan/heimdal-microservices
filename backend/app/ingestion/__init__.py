"""MQTT telemetry ingestion.

An in-process module, not a separate service (ADR-0001 modular monolith,
ADR-0009). `start()`/`stop()` are driven by the FastAPI lifespan in app.main.
The seam is deliberate: this could later become its own `python -m` entrypoint
without touching the storage or API layers.
"""

from app.ingestion.subscriber import start, stop

__all__ = ["start", "stop"]
