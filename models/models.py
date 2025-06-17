from pydantic import BaseModel


class UserFeatures(BaseModel):
    id: int
    username: str
    password: str
    email: str
    is_active: bool
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    

class UserInDB(User):
    hashed_password: str