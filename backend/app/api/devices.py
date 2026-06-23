import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.models.response import success_response
from app.services import device_service

router = APIRouter(dependencies=[Depends(get_current_user)])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("")
def create_device(payload: DeviceCreate, db: DbSession):
    device = device_service.create_device(db, payload)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device created",
        code=201,
    )


@router.get("")
def list_devices(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    devices = device_service.list_devices(db, limit=limit, offset=offset)
    return success_response(
        data=[DeviceResponse.model_validate(d).model_dump(mode="json") for d in devices],
        message="Devices retrieved",
    )


@router.get("/{device_id}")
def get_device(device_id: uuid.UUID, db: DbSession):
    device = device_service.get_device(db, device_id)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device retrieved",
    )


@router.patch("/{device_id}")
def update_device(device_id: uuid.UUID, payload: DeviceUpdate, db: DbSession):
    device = device_service.update_device(db, device_id, payload)
    return success_response(
        data=DeviceResponse.model_validate(device).model_dump(mode="json"),
        message="Device updated",
    )


@router.delete("/{device_id}")
def delete_device(device_id: uuid.UUID, db: DbSession):
    device_service.delete_device(db, device_id)
    return success_response(message="Device deleted")
