from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: UserRole = UserRole.CLIENTE

class UserCreate(UserBase):
    password: str
    tenant_id: int 

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = True
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str