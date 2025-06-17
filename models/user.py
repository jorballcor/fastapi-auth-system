from pydantic import BaseModel


class UserFeatures(BaseModel):
    id: int
    username: str
    password: str
    email: str
    is_active: bool