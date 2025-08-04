# validators.py
from pydantic import BaseModel, field_validator, EmailStr
import re
from typing import Optional


class PasswordValidator(BaseModel):
    password: str

    @field_validator("password")
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserValidator(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    password: str
    is_active: Optional[bool] = True

    @field_validator("username")
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain alphanumeric characters and underscores"
            )
        return v

    @field_validator("password")
    def validate_password(cls, v):
        return PasswordValidator(password=v).password
