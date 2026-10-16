from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str
    tenant_id: str
    user_id: str
    role: UserRole
    email: str
    full_name: str
    customer_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_id: Optional[str] = None


class DemoUser(BaseModel):
    user_id: str
    tenant_id: str
    tenant_name: str
    email: str
    full_name: str
    role: UserRole
    customer_id: Optional[str] = None
    description: str
