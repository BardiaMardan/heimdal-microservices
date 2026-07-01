import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DeviceType(str, Enum):
    """The four target domains. Stored as a plain string in the DB (not a
    Postgres ENUM) so new types are an app-level change, not a schema migration."""

    MACHINE = "machine"
    ENVIRONMENTAL = "environmental"
    FLEET = "fleet"
    STORAGE = "storage"


class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), index=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), default=DeviceStatus.INACTIVE.value)
    location: Mapped[Optional[str]] = mapped_column(String(256), default=None)
    description: Mapped[Optional[str]] = mapped_column(String(1024), default=None)

    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), default=None, index=True
    )
    hardware_id: Mapped[Optional[str]] = mapped_column(
        String(128), unique=True, index=True, default=None
    )
    device_token_hash: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def claimed(self) -> bool:
        return self.owner_id is not None


class DeviceClaim(Base):
    """Short-lived bootstrap secret binding a device to a user. The device
    generates a 6-digit code locally; only its hash is ever stored here."""

    __tablename__ = "device_claims"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), index=True
    )
    code_hash: Mapped[str] = mapped_column(String(64), index=True)
    provisioning_secret_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# --- API schemas (boundary types; never expose the ORM model directly) ---


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    type: DeviceType
    location: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1024)


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    location: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1024)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    status: str
    location: Optional[str]
    description: Optional[str]
    hardware_id: Optional[str]
    claimed: bool
    claimed_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# --- Device (provisioning) plane: unauthenticated boundary types ---

_HEX64 = Field(min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")


class AnnounceRequest(BaseModel):
    hardware_id: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=128)
    type: DeviceType
    location: Optional[str] = Field(default=None, max_length=256)
    code_hash: str = _HEX64
    provisioning_secret_hash: str = _HEX64


class AnnounceResponse(BaseModel):
    device_id: uuid.UUID
    status: str
    claimed: bool
    expires_at: Optional[datetime]


class StatusResponse(BaseModel):
    claimed: bool


class TokenRequest(BaseModel):
    hardware_id: str = Field(min_length=8, max_length=128)
    provisioning_secret: str = Field(min_length=16, max_length=128)


class TokenResponse(BaseModel):
    claimed: bool
    device_token: Optional[str] = None


# --- Operator plane: claim a device by its 6-digit code ---


class ClaimRequest(BaseModel):
    claim_code: str = Field(pattern=r"^\d{6}$")
