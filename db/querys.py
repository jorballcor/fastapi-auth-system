from fastapi import Depends
from db.access import get_db
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from db.schemas import User, Users
from models.models import UserFeatures


async def get_user(username: str, db: Depends(get_db)):
    try:
        db_user = db.query(Users).filter(User.username == username).first()
        if db_user:
            return User(
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


async def create_user_query(user: UserFeatures, db: Depends(get_db)):
    """
    Create a new user in the database.

    Args:
        user (User): The user data to be created.
        db (AsyncSession): The database session.

    Returns:
        User: The created user object.
    """
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except DatabaseConnectionError as e:
        raise e.message
