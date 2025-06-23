from db.engine import AsyncSessionLocal


async def get_db():
    """Function to get database session.

    Yields:
        AsyncSessionLocal: Asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
