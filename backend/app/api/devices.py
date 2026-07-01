import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.device import ClaimRequest, DeviceCreate, DeviceResponse, DeviceUpdate
from app.models.response import success_response
from app.models.telemetry import TelemetryPoint
from app.models.user import User
from app.services import device_service, telemetry_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("")
def create_device(payload: DeviceCreate, db: DbSession, user: CurrentUser):
    device = device_service.create_device(db, payload, owner_id=user.id)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device created",
        code=201,
    )


@router.get("")
def list_devices(
    db: DbSession,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    devices = device_service.list_devices(db, owner_id=user.id, limit=limit, offset=offset)
    return success_response(
        data=[DeviceResponse.model_validate(d).model_dump(mode="json") for d in devices],
        message="Devices retrieved",
    )


@router.post("/claim")
def claim_device(payload: ClaimRequest, db: DbSession, user: CurrentUser):
    device = device_service.claim_device(db, user.id, payload.claim_code)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device claimed",
    )


@router.get("/{device_id}")
def get_device(device_id: uuid.UUID, db: DbSession, user: CurrentUser):
    device = device_service.get_device(db, device_id, owner_id=user.id)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device retrieved",
    )


@router.get("/{device_id}/telemetry/latest")
def get_latest_telemetry(device_id: uuid.UUID, db: DbSession, user: CurrentUser):
    device_service.get_device(db, device_id, owner_id=user.id)  # owner scope
    point = telemetry_service.latest_for_device(db, device_id)
    data = TelemetryPoint.model_validate(point).model_dump(mode="json") if point else None
    return success_response(data=data, message="Latest telemetry retrieved")


@router.get("/{device_id}/telemetry")
def get_telemetry(
    device_id: uuid.UUID,
    db: DbSession,
    user: CurrentUser,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
):
    device_service.get_device(db, device_id, owner_id=user.id)  # owner scope
    points = telemetry_service.range_for_device(db, device_id, start, end, limit)
    return success_response(
        data=[TelemetryPoint.model_validate(p).model_dump(mode="json") for p in points],
        message="Telemetry retrieved",
    )


@router.patch("/{device_id}")
def update_device(device_id: uuid.UUID, payload: DeviceUpdate, db: DbSession, user: CurrentUser):
    device = device_service.update_device(db, device_id, payload, owner_id=user.id)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device updated",
    )


@router.delete("/{device_id}")
def delete_device(device_id: uuid.UUID, db: DbSession, user: CurrentUser):
    device_service.delete_device(db, device_id, owner_id=user.id)
    return success_response(message="Device deleted")
