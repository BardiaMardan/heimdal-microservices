import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import HeimdallException, NotFoundError, ValidationError
from app.models.device import (
    Device,
    DeviceClaim,
    DeviceCreate,
    DeviceStatus,
    DeviceUpdate,
)


def create_device(db: Session, payload: DeviceCreate, owner_id: int) -> Device:
    device = Device(
        name=payload.name,
        type=payload.type.value,
        status=DeviceStatus.ACTIVE.value,
        location=payload.location,
        description=payload.description,
        owner_id=owner_id,
        claimed_at=datetime.now(timezone.utc),
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def list_devices(db: Session, owner_id: int, limit: int = 100, offset: int = 0) -> list[Device]:
    stmt = (
        select(Device)
        .where(Device.owner_id == owner_id)
        .order_by(Device.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


def get_device(db: Session, device_id: uuid.UUID, owner_id: int) -> Device:
    device = db.scalars(
        select(Device).where(Device.id == device_id, Device.owner_id == owner_id)
    ).first()
    if device is None:
        raise NotFoundError(message="Device not found", details={"id": str(device_id)})
    return device


def update_device(
    db: Session, device_id: uuid.UUID, payload: DeviceUpdate, owner_id: int
) -> Device:
    device = get_device(db, device_id, owner_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(device, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: uuid.UUID, owner_id: int) -> None:
    device = get_device(db, device_id, owner_id)
    db.delete(device)
    db.commit()


def claim_device(db: Session, user_id: int, claim_code: str) -> Device:
    code_hash = security.hash_secret(claim_code)
    now = datetime.now(timezone.utc)
    claim = db.scalars(
        select(DeviceClaim).where(
            DeviceClaim.code_hash == code_hash,
            DeviceClaim.consumed_at.is_(None),
            DeviceClaim.expires_at > now,
        )
    ).first()
    if claim is None:
        raise ValidationError(message="Invalid or expired claim code")

    device = db.get(Device, claim.device_id)
    if device is None:
        raise ValidationError(message="Invalid or expired claim code")
    if device.owner_id is not None:
        raise HeimdallException(
            message="Device already claimed",
            code="DEVICE_ALREADY_CLAIMED",
            status_code=409,
        )

    device.owner_id = user_id
    device.status = DeviceStatus.ACTIVE.value
    device.claimed_at = now
    claim.consumed_at = now
    db.commit()
    db.refresh(device)
    return device
