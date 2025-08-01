import jwt

from db.access import get_db
from db.base_users_querys import get_user
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from fastapi import Depends
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from models.models import TokenData
from sqlalchemy.ext.asyncio import AsyncSession


from users.exceptions import CredentialsException
from common.config import settings, oauth2_scheme
from common.logger_config import logger


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)],):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise CredentialsException(detail=["Could not validate credentials"])
        token_data = TokenData(username=username)

    except InvalidTokenError:
        logger.info("Invalid token.")
        raise CredentialsException(detail=["Invalid token"])

    try:
        user = await get_user(username=token_data.username, db=db)
        if user is None:
            raise UserNotFoundException(username=token_data.username)
        return user

    except DatabaseConnectionError as e:
        logger.error(f"Database connection error during user lookup: {e}")
        raise DatabaseConnectionError(detail=["Database connection error"])