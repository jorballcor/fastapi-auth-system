from pydantic import BaseModel
from .validators import UserValidator


class UserCreate(UserValidator):
    pass


class UserFeatures(BaseModel):
    username: str
    password: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
