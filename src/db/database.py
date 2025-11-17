from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase

from .config_db import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,                                     # логи о БД
    # pool_size=5,                                   # подключений к бд
    # max_overflow=10,                               #10 доп подключений малоли
)

class Base(DeclarativeBase):
    pass
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT VERSION()"))
#     print(f"{result.first()=}")