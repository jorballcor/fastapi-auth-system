from fastapi import APIRouter, Depends

from typing import Annotated
from sqlalchemy.orm import Session

from db.access import get_db
from db.querys import check_existing_user, create_user_query
from db.schemas import  UsersDB
from models.models import  UserCreate, UserFeatures
from users.exceptions import CredentialsException
from users.services import (
    get_current_active_user,
    validate_user,
)


users_router = APIRouter()


@users_router.get("/users/me/", response_model=UserCreate)
async def read_users_me(
    current_user: Annotated[UserCreate, Depends(get_current_active_user)],
):
    return current_user


@users_router.post("/users/", response_model=UserCreate)
async def create_user(input_user: UserFeatures, db: Session = Depends(get_db)):
    if await check_existing_user(db, input_user.username, input_user.email):
        raise CredentialsException(detail=["Username or email already exists"])
    
    validated_user = validate_user(input_user)
    
    db_user = UsersDB(**validated_user.model_dump())
    created_user = await create_user_query(db_user, db)
    
    return created_user