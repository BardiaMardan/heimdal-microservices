import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.device import Device, DeviceStatus
from app.models.telemetry import Telemetry


class UnknownDevice(Exception):
    """Telemetry arrived for a hardware_id that maps to no claimed device.
    The subscriber drops it — this is the Phase 1 ingest boundary (ADR-0002)."""


def _claimed_device(db: Session, hardware_id: str) -> Device:
    device = db.scalars(
        select(Device).where(Device.hardware_id == hardware_id)
    ).first()
    if device is None or device.owner_id is None:
        raise UnknownDevice(hardware_id)
    return device


def record(
    db: Session, hardware_id: str, ts: datetime | None, readings: dict
) -> None:
    """Idempotently persist one reading and mark the device live. Called from the
    ingestion thread with its own Session. Raises UnknownDevice for unclaimed ids."""
    device = _claimed_device(db, hardware_id)
    now = datetime.now(timezone.utc)
    reading_ts = ts or now

    stmt = (
        insert(Telemetry)
        .values(device_id=device.id, ts=reading_ts, payload=readings)
        .on_conflict_do_nothing(index_elements=["device_id", "ts"])
    )
    db.execute(stmt)

    device.last_seen_at = now
    device.status = DeviceStatus.ACTIVE.value
    db.commit()


def mark_offline(db: Session, hardware_id: str) -> None:
    """Flip a device inactive when the broker delivers its Last Will."""
    try:
        device = _claimed_device(db, hardware_id)
    except UnknownDevice:
        return
    device.status = DeviceStatus.INACTIVE.value
    db.commit()


def latest_for_device(
    db: Session, device_id: uuid.UUID
) -> Telemetry | None:
    return db.scalars(
        select(Telemetry)
        .where(Telemetry.device_id == device_id)
        .order_by(Telemetry.ts.desc())
        .limit(1)
    ).first()


def range_for_device(
    db: Session,
    device_id: uuid.UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = 100,
) -> list[Telemetry]:
    stmt = select(Telemetry).where(Telemetry.device_id == device_id)
    if start is not None:
        stmt = stmt.where(Telemetry.ts >= start)
    if end is not None:
        stmt = stmt.where(Telemetry.ts <= end)
    stmt = stmt.order_by(Telemetry.ts.desc()).limit(limit)
    return list(db.scalars(stmt).all())
