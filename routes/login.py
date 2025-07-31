from fastapi import APIRouter, Depends

from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from db.access import get_db
from models.models import Token
from fastapi.security import OAuth2PasswordRequestForm
from users.services import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token
)
from users.exceptions import CredentialsException


login_router = APIRouter(prefix="/login")


@login_router.post("/login", response_model=Token)
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
