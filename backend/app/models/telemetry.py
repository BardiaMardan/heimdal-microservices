import uuid
from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# A single reading is a flat bag of scalars — the fields differ per device type
# (machine: temperature/vibration/rpm; fleet: speed/fuel/lat/lon; storage:
# temperature/humidity/door_open). We validate the shape, not the keys.
ReadingValue = Union[float, int, bool, str]


class Telemetry(Base):
    """One telemetry reading. Stored schema-on-read (JSONB payload) because the
    four device domains carry heterogeneous fields; see ADR-0009.

    Composite PK (device_id, ts) is both the idempotency key — a re-delivered
    QoS-1 message collides and is dropped via ON CONFLICT — and a
    Timescale-hypertable-ready layout (the partition column is in the key)."""

    __tablename__ = "telemetry"

    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True
    )
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# --- Ingestion boundary: the MQTT payload a device publishes ---


class TelemetryIngest(BaseModel):
    """Validates the JSON body on heimdall/<hardware_id>/telemetry. `ts` is
    optional; when a device omits it the subscriber stamps server time."""

    model_config = ConfigDict(extra="forbid")

    ts: datetime | None = None
    readings: dict[str, ReadingValue] = Field(min_length=1)


# --- Read boundary: what the REST API returns ---


class TelemetryPoint(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ts: datetime
    payload: dict
    ingested_at: datetime
