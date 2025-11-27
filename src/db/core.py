from .models import Base
from .database import sync_engine, async_engine

async def create_tables():
    async with async_engine.begin() as conn:
        # сначала дроп
        # print(Base.metadata.tables.keys())
        # await conn.run_sync(Base.metadata.drop_all)
        # потом создать
        await conn.run_sync(Base.metadata.create_all)