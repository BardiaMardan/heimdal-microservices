import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.device import Device, DeviceCreate, DeviceUpdate


def create_device(db: Session, payload: DeviceCreate) -> Device:
    device = Device(
        name=payload.name,
        type=payload.type.value,
        location=payload.location,
        description=payload.description,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def list_devices(db: Session, limit: int = 100, offset: int = 0) -> list[Device]:
    stmt = select(Device).order_by(Device.created_at.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def get_device(db: Session, device_id: uuid.UUID) -> Device:
    device = db.get(Device, device_id)
    if device is None:
        raise NotFoundError(message="Device not found", details={"id": str(device_id)})
    return device


def update_device(db: Session, device_id: uuid.UUID, payload: DeviceUpdate) -> Device:
    device = get_device(db, device_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(device, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: uuid.UUID) -> None:
    device = get_device(db, device_id)
    db.delete(device)
    db.commit()
