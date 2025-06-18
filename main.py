from typing import Annotated
from datetime import timedelta
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from common.db_access import get_db
from db.engine import engine
from db.schemas import Base
from db.querys import create_user_query
from models.models import UserFeatures, Token
from users.exceptions import CredentialsException
from users.services import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic 
    await engine.dispose()
    
    
app = FastAPI(lifespan=lifespan)


@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Depends(get_db())):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CredentialsException(detail=["Invalid username or password"])

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, 
                 token_type="bearer")


@app.get("/users/me/", response_model=UserFeatures)
async def read_users_me(
    current_user: Annotated[UserFeatures, Depends(get_current_active_user)],
):
    return current_user


@app.post("/users/")
async def create_user(user: UserFeatures, db: Depends(get_db()):
    create_user_query(user, db)
