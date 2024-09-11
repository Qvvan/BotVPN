from uuid import UUID
from pydantic import BaseModel
from .user import User

class VPNKeyStatus(str):
    active = "active"
    inactive = "inactive"
    expired = "expired"

class VPNKey(BaseModel):
    id: UUID
    key: str
    status: VPNKeyStatus = VPNKeyStatus.active
    user_id: UUID
