from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from db.access import get_db
from db.engine import engine, AsyncSessionLocal
from db.querys import check_existing_user, create_user_query
from db.schemas import Base, UsersDB
from models.models import Token, UserCreate, UserFeatures
from users.exceptions import CredentialsException
from users.helper import get_password_hash
from users.services import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_initial_admin_user,
    get_current_active_user,
    validate_user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            await create_initial_admin_user(session)
    yield
    # Shutdown logic
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/login", response_model=Token)
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


@app.get("/users/me/", response_model=UserCreate)
async def read_users_me(
    current_user: Annotated[UserCreate, Depends(get_current_active_user)],
):
    return current_user


@app.post("/users/", response_model=UserCreate)
async def create_user(input_user: UserFeatures, db: Session = Depends(get_db)):
    if await check_existing_user(db, input_user.username, input_user.email):
        raise CredentialsException(detail=["Username or email already exists"])
    
    
    validated_user = validate_user(input_user)
    
    db_user = UsersDB(**validated_user.model_dump())
    created_user = await create_user_query(db_user, db)
    
    return created_user
