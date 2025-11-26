import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
from src.app.delete_msg import delete_last_bot_message
from aiogram.fsm.context import FSMContext
from src.app.models import Homework
from src.app.states import HomeworkStates

router = Router(name="homework")
media_groups_temp = {}
MEDIA_GROUP_TIMEOUT = 2

@router.message(Command('homework'))
async def get_homework(message : Message, state : FSMContext):
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

    try:
        deadline_date = datetime.strptime(message.text, "%H:%M %d.%m.%y")
        if deadline_date < datetime.now():
            raise ValueError("Дедлайн в прошлое?")
        hw.deadline = deadline_date.strftime("%d.%m.%y %H:%M")
        await state.update_data(homework=hw.to_dict())
        await message.answer(
            f"Домашнее задание сохранено!\n"
            f"Предмет: {hw.subject}\n"
            f"Текст: {hw.text if hw.text else 'Нет'}\n"
            f"Дедлайн: {hw.deadline}\n\n"
        )
        await state.update_data(last_bot_message_id=None)
        await message.delete()
    except Exception:
        msg = await message.answer("Что-то не то с дедлайном(")
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()