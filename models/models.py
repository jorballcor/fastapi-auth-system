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


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    done: bool = False
    
    
class TodoResponse(BaseModel):
    title: str
    description: str | None = None
    done: bool
    owner_id: int

    class Config:
        orm_mode = True
        
    
class TodoUpdate(BaseModel):        
    title: str | None = None
    description: str | None = None
    done: bool | None = None