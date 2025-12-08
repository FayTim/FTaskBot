from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from src.app.delete_msg import delete_last_bot_message
from aiogram.fsm.context import FSMContext
from src.app.models import Homework
from src.app.states import HomeworkStates
from src.db.metods_db_homework import send_homework
from src.db.metods_db_settings import get_settings_chat

router = Router(name="homework")
media_groups_temp = {}
MEDIA_GROUP_TIMEOUT = 2

@router.message(Command('homework'))
async def get_homework(message : Message, state : FSMContext):
    if await get_settings_chat(message.chat.id) is None:
        msg = await message.answer('Сначала настройте бота!')
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return
    hw = Homework(subject="example")
    await state.update_data(homework=hw.to_dict())
    await state.set_state(HomeworkStates.homework_data)

    msg = await message.answer('Отправьте текст задания, фото, ссылку или pdf')

    await state.update_data(last_bot_message_id=msg.message_id)
    await message.delete()

@router.message(HomeworkStates.homework_data, F.text)
async def get_text(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)

    data = await state.get_data()
    hw = Homework(**data.get("homework"))
    hw.text = message.text

    await state.update_data(homework=hw.to_dict())
    await state.set_state(HomeworkStates.deadline)

    msg = await message.answer("Напишите дедлайн задания в формате: hh:mm dd.mm.yy")
    await state.update_data(last_bot_message_id=msg.message_id)

    await message.delete()

@router.message(HomeworkStates.deadline)
async def get_deadline(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)

    data = await state.get_data()
    hw = Homework(**data.get("homework"))
    deadline_date = None
    try:
        deadline_date = datetime.strptime(message.text, "%H:%M %d.%m.%y")
        if deadline_date < datetime.now():
            raise ValueError("Дедлайн в прошлое?")
        hw.deadline = deadline_date.strftime("%d.%m.%y %H:%M")
        await state.update_data(homework=hw.to_dict())
        await send_homework(message.chat.id, hw.text, deadline_date)
        await message.answer(
            f"Домашнее задание сохранено!\n"
            f"Текст: {hw.text if hw.text else 'Нет'}\n"
            f"Дедлайн: {hw.deadline}\n\n"
        )
        await state.clear()
        await state.update_data(last_bot_message_id=None)
        await message.delete()
    except Exception as e:
        msg = await message.answer(f"Что-то не то с дедлайном(\n"
                                   f"Ваш ввод: {deadline_date}")
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()