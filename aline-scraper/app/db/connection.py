from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost/scraper_db')

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def get_session():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()