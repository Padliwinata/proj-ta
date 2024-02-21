from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, SecretStr, Field


class UserRole(str, Enum):
    admin = "admin"
    super_admin = "super admin"
    staff = "staff"


class RegisterForm(BaseModel):
    username: str
    email: str
    password: SecretStr


class Response(BaseModel):
    success: bool
    code: int
    message: str
    data: Optional[Dict[str, Any]]


class User(BaseModel):
    username: str
    email: str
    password: SecretStr
    role: UserRole = UserRole.admin


class Refresh(BaseModel):
    refresh_token: str

