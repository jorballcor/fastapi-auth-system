from datetime import datetime, timedelta, timezone

import jwt
from exceptions import CredentialsException, InactiveUserException
from fastapi import Annotated, Depends
from helper import verify_password
from jwt.exceptions import InvalidTokenError

from db.access import get_db
from common.logger_config import logger
from common.config import settings
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from db.querys import get_user
from models.models import TokenData, UserFeatures
from users.helper import oauth2_scheme

ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def authenticate_user(username: str, password: str, db: Depends(get_db)):
    user = get_user(username, db)
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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise CredentialsException(detail=["Could not validate credentials"])
        token_data = TokenData(username=username)

    except InvalidTokenError:
        logger.info("Invalid token.")
        raise CredentialsException(detail=["Invalid token"])

    try:
        user = get_user(username=token_data.username, db=Depends(get_db))
        if user is None:
            raise UserNotFoundException(username=token_data.username)
        return user

    except DatabaseConnectionError as e:
        logger.error(f"Database connection error during user lookup: {e}")
        raise CredentialsException(detail=["Database connection error"])


async def get_current_active_user(
    current_user: Annotated[UserFeatures, Depends(get_current_user)],
):
    if current_user.is_active is False:
        raise InactiveUserException
    return current_user
