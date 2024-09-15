from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Users(BaseModel):
    tg_id: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Service(BaseModel):
    id: str
    name: str
    duration_days: int
    price: int


class VPNKey(BaseModel):
    id: str = Field(default_factory=str)
    key: str = Field(default_factory=str)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: int
    is_blocked: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Subscription(BaseModel):
    tg_id: str
    service_id: str
    vpn_key_id: str
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Log(BaseModel):
    id: str
    tg_id: str
    action: str
    details: dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Transaction(BaseModel):
    transaction_id: str
    service_id: str
    tg_id: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
