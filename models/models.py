from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Users(BaseModel):
    tg_id: int
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Service(BaseModel):
    id: int
    name: str
    duration_days: int
    price: int


class VPNKey(BaseModel):
    id: int
    key: str = ''
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: int
    is_blocked: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Subscription(BaseModel):
    id: int
    tg_id: int
    service_id: int
    vpn_key_id: int
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Log(BaseModel):
    id: int
    tg_id: int
    action: str
    details: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(BaseModel):
    id: int
    transaction_id: str
    service_id: str
    tg_id: int
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
