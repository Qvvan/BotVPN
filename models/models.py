from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Users(BaseModel):
    tg_id: int
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    duration_days: int
    price: int


class VPNKey(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    key: str
    issued_at: Optional[datetime] = None
    is_active: bool = False
    is_blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Subscription(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tg_id: int
    service_id: UUID
    vpn_key_id: UUID
    start_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Log(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tg_id: int
    action: str
    details: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    transaction_id: str
    service_id: str
    tg_id: int
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
