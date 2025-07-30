from fastapi import APIRouter, Depends
from models.models import Token

from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from db.access import get_db
from db.querys import check_existing_user, create_user_query
from db.schemas import  UsersDB
from models.models import Token, UserCreate, UserFeatures
from users.exceptions import CredentialsException
from users.services import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    validate_user,
)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CredentialsException(detail=["Invalid username or password"])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserCreate)
async def read_users_me(
    current_user: Annotated[UserCreate, Depends(get_current_active_user)],
):
    return current_user


@router.post("/users/", response_model=UserCreate)
async def create_user(input_user: UserFeatures, db: Session = Depends(get_db)):
    if await check_existing_user(db, input_user.username, input_user.email):
        raise CredentialsException(detail=["Username or email already exists"])
    
    
    validated_user = validate_user(input_user)
    
    db_user = UsersDB(**validated_user.model_dump())
    created_user = await create_user_query(db_user, db)
    
    return created_user
