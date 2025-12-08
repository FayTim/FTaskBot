from src.db.core import create_tables
from aiogram import Bot, Dispatcher
import asyncio
from src.app.settings import router as settings_router
from src.app.homework import router as homework_router
from src.app.test import router as test_router
from config import TOKEN
bot = Bot(TOKEN)
dp = Dispatcher()


async def main():
    print(1)
    dp.include_router(test_router)
    dp.include_router(settings_router)
    dp.include_router(homework_router)
    await create_tables()
    print(52)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())