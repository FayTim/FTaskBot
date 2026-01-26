from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
from src.app.delete_msg import delete_last_bot_message
from aiogram.fsm.context import FSMContext
from src.app.states import HomeworkStates
from src.db.metods_db_homework import send_homework
from src.db.metods_db_settings import get_settings_chat

router = Router(name="homework")

@router.message(Command('homework'))
async def get_homework(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)

    if await get_settings_chat(message.chat.id) is None:
        msg = await message.answer('Сначала настройте бота!')
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    msg = await message.answer('Введите суть задания \nНапример: Задачи из Демидовича',
                               reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_settings")],
                ])
    )

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(HomeworkStates.homework_title)
    await message.delete()

@router.message(HomeworkStates.homework_title, F.text)
async def get_title_homework(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)
    title = message.text.strip()
    msg = await message.answer('Отправьте теперь само задание или ссылку на него')

    await state.update_data(homework_title=title)
    await state.set_state(HomeworkStates.homework_data)

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(HomeworkStates.homework_data)
    await message.delete()


@router.message(HomeworkStates.homework_data, F.text)
async def get_homework(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)
    description = message.text.strip()
    msg = await message.answer("Напишите дедлайн задания в формате: hh:mm dd.mm.yy \n"
                               "Например 12:00 25.12.25")

    await state.update_data(homework_data=description)
    await state.set_state(HomeworkStates.deadline)

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(HomeworkStates.deadline)
    await message.delete()

@router.message(HomeworkStates.deadline, F.text)
async def get_deadline(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)
    chat_id = message.chat.id
    deadline = message.text
    try:
        deadline_date = datetime.strptime(deadline, "%H:%M %d.%m.%y")
        if deadline_date < datetime.now():
            msg = await message.answer(f"Дедлайн в прошлое?\n"
                                       f"Ваш ввод: {deadline} \n"
                                       f"Формат дедлайна: hh:mm dd.mm.yy \n"
                                       f"Попробуйте снова😔")
            await state.update_data(last_bot_message_id=msg.message_id)
            await message.delete()
            return

        deadline = deadline_date.strftime("%d.%m.%y %H:%M")
        await state.update_data(deadline=deadline_date)
        data = await state.get_data()
        await send_homework(chat_id, data)
        title = data["homework_title"]
        text = data["homework_data"]
        await message.answer(
            f"Домашнее задание сохранено!\n"
            f"Заголовок📋: {title} \n"
            f"Описание📝: {text if text else 'Нет'}\n"
            f"Дедлайн🕔: {deadline}\n\n"
        )
        await state.clear()
        await state.update_data(last_bot_message_id=None)
        await message.delete()
    except Exception:
        msg = await message.answer(f"Что-то не то с дедлайном(\n"
                                   f"Ваш ввод: {deadline} \n"
                                   f"Формат дедлайна: hh:mm dd.mm.yy \n"
                                   f"Попробуйте снова😔")
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()

@router.callback_query(HomeworkStates.homework_title, F.data == "cancel_settings")
async def settings_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.clear()