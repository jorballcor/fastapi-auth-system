import asyncio
import os
import sys
from common.logger_config import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from db.engine import engine
from db.schemas import Base


async def reset_db():
    logger.info(" Dropping and recreating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    logger.info(" Database reset complete.")


if __name__ == "__main__":
    asyncio.run(reset_db())
