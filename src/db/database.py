from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config_db import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,                                     # логи о БД
    # pool_size=5,                                   # подключений к бд
    # max_overflow=10,                               #10 доп подключений малоли
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,                                     # логи о БД
    # pool_size=5,                                   # подключений к бд
    # max_overflow=10,                               #10 доп подключений малоли
)
async_session_factory = async_sessionmaker(async_engine)

class Base(DeclarativeBase):
    pass

