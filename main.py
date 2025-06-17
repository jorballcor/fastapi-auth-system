from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db.common import get_db
from db.engine import engine
from db.schemas import Base, User
from models.services import create_user_query
from models.models import User
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

@app.post("/users/")
async def create_user(user: User, db: Depends(get_db)):
    create_user_query(user: User, db: db)
