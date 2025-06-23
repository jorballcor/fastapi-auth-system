from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from common.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, pool_recycle=3600)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
