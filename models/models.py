from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Service(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    duration_days: int
    price_stars: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Payment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tg_id: int
    service_id: UUID
    amount_stars: int
    status: str
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VPNKey(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    key: str
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
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
    end_date: datetime
    auto_renewal: bool = False
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
    payment_id: UUID
    status: str
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
