from fastapi import Depends
from db.common import get_db
from db.schemas import User


async def create_user_query(user: User, db: Depends(get_db)):
    """
    Create a new user in the database.
    
    Args:
        user (User): The user data to be created.
        db (AsyncSession): The database session.
    
    Returns:
        User: The created user object.
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user