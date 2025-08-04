from datetime import datetime, timedelta, timezone

import jwt
from db.base_users_querys import get_user
from fastapi import Depends
from typing import Annotated


from db.access import get_db
from common.logger_config import logger
from models.models import UserCreate, UserFeatures
from users.dependencies import get_current_user
from users.helper import get_password_hash, verify_password
from users.exceptions import CredentialsException, InactiveUserException
from common.config import settings


ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


SUPERUSER_USERNAME = settings.FIRST_SUPERUSER_USERNAME
SUPERUSER_EMAIL = settings.FIRST_SUPERUSER_EMAIL
SUPERUSER_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD


async def authenticate_user(username: str, password: str, db: Depends(get_db)):
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_active_user(
    current_user: Annotated[UserCreate, Depends(get_current_user)],
):
    if current_user.is_active is False:
        raise InactiveUserException
    return current_user


def validate_user(user: UserFeatures) -> UserCreate:
    try:
        validated_user = UserCreate(
            username=user.username,
            email=user.email,
            password=user.password,
        )   
                
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise CredentialsException(detail=["Invalid user data"])
    
    validated_user.password = get_password_hash(validated_user.password)
    
    return validated_user