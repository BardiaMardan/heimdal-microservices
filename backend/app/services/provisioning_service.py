from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import NotFoundError
from app.models.device import (
    AnnounceRequest,
    Device,
    DeviceClaim,
    DeviceStatus,
)

CLAIM_TTL = timedelta(minutes=10)


def announce(db: Session, payload: AnnounceRequest) -> tuple[Device, DeviceClaim | None]:
    now = datetime.now(timezone.utc)
    device = db.scalars(
        select(Device).where(Device.hardware_id == payload.hardware_id)
    ).first()

    if device is not None and device.owner_id is not None:
        device.last_seen_at = now
        db.commit()
        db.refresh(device)
        return device, None

    if device is None:
        device = Device(
            name=payload.name,
            type=payload.type.value,
            status=DeviceStatus.INACTIVE.value,
            location=payload.location,
            hardware_id=payload.hardware_id,
            last_seen_at=now,
        )
        db.add(device)
        db.flush()
    else:
        device.last_seen_at = now

    for stale in db.scalars(
        select(DeviceClaim).where(
            DeviceClaim.device_id == device.id,
            DeviceClaim.consumed_at.is_(None),
        )
    ).all():
        stale.consumed_at = now

    claim = DeviceClaim(
        device_id=device.id,
        code_hash=payload.code_hash,
        provisioning_secret_hash=payload.provisioning_secret_hash,
        expires_at=now + CLAIM_TTL,
    )
    db.add(claim)
    db.commit()
    db.refresh(device)
    db.refresh(claim)
    return device, claim


def get_status(db: Session, hardware_id: str) -> bool:
    device = db.scalars(
        select(Device).where(Device.hardware_id == hardware_id)
    ).first()
    if device is None:
        raise NotFoundError(message="Device not found")
    return device.owner_id is not None


def issue_token(db: Session, hardware_id: str, provisioning_secret: str) -> tuple[bool, str | None]:
    device = db.scalars(
        select(Device).where(Device.hardware_id == hardware_id).with_for_update()
    ).first()
    if device is None:
        raise NotFoundError(message="Device not found")

    if device.owner_id is None:
        db.commit()
        return False, None

    secret_hash = security.hash_secret(provisioning_secret)
    valid_secret = db.scalars(
        select(DeviceClaim).where(
            DeviceClaim.device_id == device.id,
            DeviceClaim.provisioning_secret_hash == secret_hash,
        )
    ).first()
    if valid_secret is None:
        db.commit()
        return True, None

    if device.device_token_hash is not None:
        db.commit()
        return True, None

    token = security.generate_device_token()
    device.device_token_hash = security.hash_secret(token)
    db.commit()
    return True, token
