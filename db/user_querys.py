from fastapi import Depends
from sqlalchemy import select

from db.access import get_db
from db.exceptions import DatabaseConnectionError
from db.schemas import UsersDB
from models.models import UserCreate
from sqlalchemy import select
from db.engine import AsyncSessionLocal
from users.helper import get_password_hash
from common.logger_config import logger
from users.services import SUPERUSER_EMAIL, SUPERUSER_PASSWORD, SUPERUSER_USERNAME


async def create_user_query(user: UserCreate, db: Depends(get_db)):
    """
    Create a new user in the database.

    Args:
        user (UserFeatures): The user data to be created.
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

async def check_existing_user(db: Depends(get_db), username: str, email: str) -> bool:
    existing_user = await db.execute(
        select(UsersDB).where(
            (UsersDB.username == username) | 
            (UsersDB.email == email)
        )
    )
    return existing_user.scalars().first() is not None




async def create_initial_admin_user(db: AsyncSessionLocal()):
    try:
        result = await db.execute(select(UsersDB).limit(1))
        first_user = result.scalar_one_or_none()
        if first_user:
            #logger.info("Un utilisateur existe déjà, aucun admin initial créé.")
            return

        first_user = UsersDB(
            username=SUPERUSER_USERNAME,
            email=SUPERUSER_EMAIL,
            password=get_password_hash(SUPERUSER_PASSWORD),
            is_active=True,
        )
        db.add(first_user)
        await db.commit()
        logger.info("Utilisateur admin initial créé")
    except Exception as e:
        logger.error(f"Échec de la création de l'utilisateur admin initial : {e}")


