from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from aiogram.filters import Command

from app.delete_msg import delete_last_bot_message
from app.states import SettingsStates

router = Router(name="settings")

chat_settings = {}
current = None

@router.message(Command('settings'))
async def get_settings(message : Message, state : FSMContext, bot: Bot):

    chat_id = message.chat.id

    existing = chat_settings.get(chat_id)

    if existing is None or existing.get("active") is True:

        msg = await message.answer("Привет👋 \n"
                                   "Добро пожаловать в настройки бота \n"
                                   "Для начала давай впишем ФИО преподавателя")

    else:
        msg = await message.answer("Хотите изменить настройки?🤔 \n"
                                   "А вот хуй вам пока что, но Тимурка скоро сделает")

    chat_settings[chat_id] = {
        "teacher": None,
        "subject": None,
        "group_students": [],
        "poll_message_id": None,
        "active": True,
    }

    await state.set_state(SettingsStates.teacher)
    await state.update_data(last_bot_message_id=msg.message_id)
    await message.delete()
    print(f"[FSM] Текущее состояние: {await state.get_state()}\n")

@router.message(F.text, SettingsStates.teacher)
async def get_settings_subject(message : Message, state : FSMContext, bot: Bot):
    chat_id = message.chat.id
    teacher_name = message.text.strip()

    chat_settings[chat_id]['teacher'] = message.text

    await state.update_data(teacher=message.text)
    await delete_last_bot_message(message, state)

    msg = await message.answer("Хорошо, теперь впишем название предмета, который вы изучаете")

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.subject)
    await message.delete()

    print(f"[SETTINGS] Teacher='{teacher_name}' для чата {chat_id}")
    print(f"[FSM] state={await state.get_state()} data={await state.get_data()}\n")

@router.message(F.text, SettingsStates.subject)
async def get_group_list(message: Message, state: FSMContext):
    chat_id = message.chat.id
    subject_name = message.text.strip()

    chat_settings[chat_id]["subject"] = subject_name
    await state.update_data(subject=subject_name)

    await delete_last_bot_message(message, state)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Хочу получать ДЗ в приложении", callback_data="yes")],
        [InlineKeyboardButton(text="Не хочу получать ДЗ в приложении", callback_data="no")]
    ])
    msg = await message.answer(
        f"Отлично! Предмет: {subject_name}\n"
        f"Теперь пусть участники выберут, хотят ли получать домашки в приложении 👇",
        reply_markup=keyboard
    )
    chat_settings[chat_id]['poll_message_id'] = msg.message_id
    await message.delete()
    # await state.update_data(last_bot_message_id=msg.message_id)
    await state.clear()
    # await state.set_state(SettingsStates.group_list)

    print(f"[SETTINGS] Subject='{subject_name}' для чата {chat_id}")
    print(f"[DEBUG] Ожидаем ответы от участников чата {chat_id}\n")

@router.callback_query(F.data.in_(["yes", "no"]))
async def get_group_list(callback: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    username = callback.from_user.full_name
    choice = callback.data

    await callback.answer()

    if chat_id not in chat_settings:
        print(f"[WARN] Ответ '{choice}' получен без активных настроек в чате {chat_id}")
        return

    group_students = chat_settings[chat_id]['group_students']
    if any(student[0] == user_id for student in group_students):
        print(f"[SKIP] {username} уже голосовал")
        return
    group_students.append((user_id, choice == "yes"))
    print(f"[VOTE] {username} ({user_id}) → {choice}")

    if len(group_students) >= await bot.get_chat_member_count(chat_id=chat_id) - 1:
        await callback.message.delete()
        chat_settings[chat_id]["active"] = True
        await bot.send_message(
            chat_id,
            "✅ Настройки завершены!\nВсе участники ответили."
        )
        print(f"[DONE] Настройки завершены для чата {chat_id}")
        print(f"[RESULT] {chat_settings[chat_id]}\n")

