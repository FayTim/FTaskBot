from aiogram import Bot, Dispatcher
import asyncio
from src.app.settings import router as settings_router
from src.app.homework import router as homework_router
from src.app.test import router as test_router
from src.config import TOKEN
bot = Bot(TOKEN)
dp = Dispatcher()

# @dp.message(CommandStart)
# async def r(message: Message):
#     await message.answer("Работает?")



# if __name__ == "__main__":
#     asyncio.run(main())
    # from datetime import datetime
    # date_input = input()
    # date = datetime.strptime(date_input, "%H:%M %d.%m.%y")
    # if date < datetime.now():
    #     print(58)
