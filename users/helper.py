from db.common import get_db
from db.exceptions import DatabaseConnectionError, UserNotFoundException
from db.schemas import User
from fastapi import Depends
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: Depends = get_db()):
    try:
        db_user = db.query(User).filter(User.username == username).first()
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