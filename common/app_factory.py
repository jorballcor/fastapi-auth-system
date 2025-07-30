from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.engine import engine, AsyncSessionLocal
from db.schemas import Base
from users.services import create_initial_admin_user
from routes import router


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
    
    
def create_app(testing: bool = False) -> FastAPI:
    if testing:
        app = FastAPI()
        app.include_router(router)
        return app
    
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    return app