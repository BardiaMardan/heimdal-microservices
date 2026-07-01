from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.device import AnnounceRequest, TokenRequest
from app.models.response import success_response
from app.services import provisioning_service

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]


@router.post("/announce")
def announce(payload: AnnounceRequest, db: DbSession):
    device, claim = provisioning_service.announce(db, payload)
    return success_response(
        data={
            "device_id": str(device.id),
            "status": device.status,
            "claimed": device.claimed,
            "expires_at": claim.expires_at.isoformat() if claim else None,
        },
        message="Device announced",
    )


@router.get("/status")
def status(db: DbSession, hardware_id: Annotated[str, Query(min_length=8, max_length=128)]):
    claimed = provisioning_service.get_status(db, hardware_id)
    return success_response(data={"claimed": claimed}, message="Status retrieved")


@router.post("/token")
def token(payload: TokenRequest, db: DbSession):
    claimed, device_token = provisioning_service.issue_token(
        db, payload.hardware_id, payload.provisioning_secret
    )
    return success_response(
        data={"claimed": claimed, "device_token": device_token},
        message="Token issued" if device_token else "No token issued",
    )
