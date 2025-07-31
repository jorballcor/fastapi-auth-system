import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text 
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from db.schemas import Base, UsersDB 
from db.access import get_db 
from common.app_factory import create_app
from common.config import settings
from users.helper import get_password_hash


TEST_DATABASE_URL = settings.TEST_DATABASE_URL
FIRST_SUPERUSER_USERNAME = settings.FIRST_SUPERUSER_USERNAME
FIRST_SUPERUSER_EMAIL = settings.FIRST_SUPERUSER_EMAIL
FIRST_SUPERUSER_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD


app_testing = create_app(testing=settings.TESTING)


engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=AsyncSession
)


# 👉 Override de la dépendance get_db
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app_testing.dependency_overrides[get_db] = override_get_db


# 👉 Initialisation des tables au début des tests
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
def client():
    asyncio.run(init_db())  # crée les tables avant d'exécuter les tests
    asyncio.run(seed_admin()) 
    with TestClient(app_testing) as c:
        yield c


async def seed_admin():
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"DELETE FROM {table.name}"))

    async with TestingSessionLocal() as session:
        user = UsersDB(
            username=FIRST_SUPERUSER_USERNAME,
            email=FIRST_SUPERUSER_EMAIL,
            password=get_password_hash(FIRST_SUPERUSER_PASSWORD),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        

async def init_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)   # optionnel si tu veux reset
        await conn.run_sync(Base.metadata.create_all)