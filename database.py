import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:root@localhost:5432/postgres")
# 1. Build the absolute path to your base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. Tell load_dotenv exactly where to look
load_dotenv(os.path.join(BASE_DIR, ".env"))


engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600, echo=False)
async_session = async_sessionmaker(engine)

Base = declarative_base()

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
