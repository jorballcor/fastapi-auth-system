from db.access import get_db
from db.schemas import Base, UsersDB
import pytest
import asyncio


from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
from sqlalchemy import text 
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from common.app_factory import create_app
from common.config import settings
from common.logger_config import logger
from users.helper import get_password_hash


TEST_DATABASE_URL = settings.TEST_DATABASE_URL
FIRST_SUPERUSER_USERNAME = settings.FIRST_SUPERUSER_USERNAME
FIRST_SUPERUSER_EMAIL = settings.FIRST_SUPERUSER_EMAIL
FIRST_SUPERUSER_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD


app_testing = create_app(testing=settings.TESTING)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app_testing.dependency_overrides[get_db] = override_get_db


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
        await conn.run_sync(Base.metadata.drop_all)  
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module")
def client():
    asyncio.run(init_db())  
    asyncio.run(seed_admin()) 
    
    with TestClient(app_testing) as c:
        yield c
        
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture
def auth_headers(client: TestClient):
    # Login to get token
    login_response = client.post("/login", data={
        "username": FIRST_SUPERUSER_USERNAME,
        "password": FIRST_SUPERUSER_PASSWORD
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def pytest_sessionstart(session):
    """Validate test config before running tests"""
    if not settings.TESTING:
        pytest.exit("TESTING must be True for tests", returncode=1)