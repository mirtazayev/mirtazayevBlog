from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use asyncpg for PostgreSQL
DATABASE_URL = "postgresql+asyncpg://mirtazayev:npg_wikJ0dsH1tzv@ep-divine-art-a4pbs04v.us-east-1.pg.koyeb.app/koyebdb"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=25,
    max_overflow=20,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
