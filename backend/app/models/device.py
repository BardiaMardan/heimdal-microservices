import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, String, func
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
    status: Mapped[str] = mapped_column(String(32), default=DeviceStatus.ACTIVE.value)
    location: Mapped[Optional[str]] = mapped_column(String(256), default=None)
    description: Mapped[Optional[str]] = mapped_column(String(1024), default=None)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
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
    last_seen_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
