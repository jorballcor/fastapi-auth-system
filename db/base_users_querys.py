from fastapi import Depends
from sqlalchemy import select
from db.access import get_db
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from db.schemas import  UsersDB
from models.models import UserCreate
from db.exceptions import DatabaseConnectionError, UserNotFoundException


async def get_user(username: str, db: Depends(get_db)):
    try:
        stmt = select(UsersDB).where(UsersDB.username == username)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()

        if db_user:
            return UserCreate(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                is_active=db_user.is_active,
                password=db_user.password,
            )

        else:
            raise UserNotFoundException(username)

    except DatabaseConnectionError as e:
        raise e.message
