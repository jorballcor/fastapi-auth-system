from ast import List
from fastapi import HTTPException, status



class CredentialsException(HTTPException):
    def __init__(self, detail: List[str] = ["Could not validate credentials", "Invalid username or password"]):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
 

class InactiveUserException(HTTPException):
    def __init__(self, detail: List[str] = ["Inactive user"]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )