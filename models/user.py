from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: UUID = Field(default_factory=UUID)
    username: str
    email: EmailStr
    is_active: bool = True
