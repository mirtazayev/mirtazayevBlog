from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# PostgreSQL database URL
DATABASE_URL = "postgresql://mirtazayev:npg_wikJ0dsH1tzv@ep-divine-art-a4pbs04v.us-east-1.pg.koyeb.app/koyebdb"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization failed: {e}")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
