import re

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from src.app.delete_msg import delete_last_bot_message
from src.app.states import SettingsStates

from src.db.metods_db_settings import *

router = Router(name="settings")
settings = {}
@router.message(Command('settings'))
async def get_settings(message : Message, state : FSMContext):
    chat_id = message.chat.id
    if await get_settings_chat(chat_id) is None:
        msg = await message.answer("Привет👋 \n"
                                   "Добро пожаловать в настройки бота \n"
                                   "Для начала давай впишем ФИО преподавателя👨‍🏫")

        await state.set_state(SettingsStates.teacher)
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await message.delete()
    else:
        msg = await message.answer("Настройки для этого чата уже есть\n"
                                   "Что вы хотите изменить?",
                                   reply_markup=settings_menu_kb())
        await state.set_state(SettingsStates.menu)  # добавь новое состояние menu
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await message.delete()

@router.message(F.text, SettingsStates.teacher)
async def get_teacher(message : Message, state : FSMContext):
    teacher = message.text.strip()
    if not re.fullmatch(r'([А-ЯЁа-яё]+) ([А-ЯЁа-яё]+) ([А-ЯЁа-яё]+)', teacher):
        msg = await message.answer("Что-то не то с вводом(\n"
                                   f"Ваш ввод: {teacher}\n"
                                   "Введите пожалуйста ФИО, ещё раз")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(teacher=teacher)
    await delete_last_bot_message(message, state)

    if edit_field == "teacher":
        chat_id = message.chat.id
        await update_teacher_in_db(chat_id, new_teacher_name=teacher)  # функция обновления в БД

        msg = await message.answer(
            "ФИО преподавателя обновлено ✅"
        )
        await state.update_data(last_bot_message_id=msg.message_id,
                               edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        msg = await message.answer("Давай также впишем контакт преподавателя 📧 (это может быть ник в телеграмм или почта, или что-то еще)")

        await state.update_data(last_bot_message_id=msg.message_id)
        await state.set_state(SettingsStates.teacher_email)
        await message.delete()
    print(f"[FSM] state={await state.get_state()} data={await state.get_data()}\n")

@router.message(F.text, SettingsStates.teacher_email)
async def get_teacher_email(message : Message, state : FSMContext):
    email = message.text
    if (not re.fullmatch(r'(\S+)@(\w+)\.(\w{2,3})', email) and
            not re.fullmatch(r'^(\+7|8)\d{10}', email) and
            not re.fullmatch(r'@(\w+)', email)):
        msg = await message.answer("Некорректный контакт( \n"
                                   f"Ваш ввод: {email}\n"
                                   f"Попробуйте еще раз")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(teacher_email=email)
    await delete_last_bot_message(message, state)

    if edit_field == "teacher_email":
        chat_id = message.chat.id
        await update_teacher_email_in_db(chat_id, teacher_email=email)
        msg = await message.answer("Контакт преподавателя обновлен ✅")
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        msg = await message.answer("Хорошо, теперь впишем название предмета, который вы изучаете 📚")

        await state.update_data(last_bot_message_id=msg.message_id)
        await state.set_state(SettingsStates.subject)
        await message.delete()


@router.message(F.text, SettingsStates.subject)
async def get_subject(message: Message, state: FSMContext):
    subject = message.text.strip()
    if not re.fullmatch(r'[А-ЯЁа-яё ]+', subject):
        msg = await message.answer("Что не так написано в предмете\n"
                                   f"Ваш ввод: {subject}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(subject=subject)
    await delete_last_bot_message(message, state)
    if edit_field == "subject":
        chat_id = message.chat.id
        await update_subject_in_db(chat_id, subject)
        msg = await message.answer("Название предмета обновлено ✅")
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        msg = await message.answer("Впишите номер студенческой группы в сокращенном виде (ФТ-101, ФТ-204)👥")

        await state.update_data(last_bot_message_id=msg.message_id)
        await state.set_state(SettingsStates.group_number)
        await message.delete()


@router.message(F.text, SettingsStates.group_number)
async def get_group_number(message: Message, state: FSMContext):
    group = message.text.strip()
    if not re.fullmatch(r'ФТ-(\d{3})', group):
        msg = await message.answer("Что не так в номере вашей группы(\n"
                                   f"Ваш ввод: {group}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(group_number=group)
    await delete_last_bot_message(message, state)

    if edit_field == "group_number":
        chat_id = message.chat.id
        await update_group_number_in_db(chat_id, group)
        msg = await message.answer("Номер группы обновлен ✅")
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        msg = await message.answer("Впишите номер подгруппы для которой предназначен этот предмет"
                             "Если для всей группы введите просто 0 😊")
        await state.update_data(last_bot_message_id=msg.message_id)
        await state.set_state(SettingsStates.subgroup_number)
        await message.delete()

@router.message(F.text, SettingsStates.subgroup_number)
async def get_subgroup_number(message: Message, state: FSMContext):
    subgroup = message.text.strip()
    if not re.fullmatch('[0-2]', subgroup):
        msg = await message.answer("Что не так в номере вашей подгруппы(\n"
                                   f"Ваш ввод: {subgroup}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(subgroup_number=subgroup)
    await delete_last_bot_message(message, state)

    if edit_field == "subgroup_number":
        chat_id = message.chat.id
        await update_subgroup_number_in_db(chat_id, subgroup)
        msg = await message.answer("Номер подгруппы обновлён ✅")
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        msg = await message.answer("И последняя настройка\n"
                                   "Введите ссылку на регламент по предмету")
        await state.update_data(last_bot_message_id=msg.message_id)
        await state.set_state(SettingsStates.regulation_link)
        await message.delete()

@router.message(F.text, SettingsStates.regulation_link)
async def get_regulation(message: Message, state: FSMContext):
    regulation_link = message.text.strip()
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', regulation_link):
        msg = await message.answer("Что не так в ссылке на регламент(\n"
                                   f"Ваша ссылка: {regulation_link}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")

    await state.update_data(regulation_link=regulation_link)
    await delete_last_bot_message(message, state)

    chat_id = message.chat.id
    if edit_field == "regulation_link":
        await update_regulation_db(chat_id, regulation_link)
        msg = await message.answer("Ссылка на регламент обновлена ✅")
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await state.set_state(SettingsStates.menu)
        await message.delete()
    else:
        data = await state.get_data()
        await save_chat_settings(chat_id, data)

        msg = await message.answer("Спасибо! Настройки завершены 😊")
        await state.update_data(last_bot_message_id=msg.message_id)
        await state.clear()
        await message.delete()

def settings_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🏫 ФИО преподавателя", callback_data="edit_teacher")],
            [InlineKeyboardButton(text="📧 Контакт преподавателя", callback_data="edit_teacher_email")],
            [InlineKeyboardButton(text="📚 Название предмета", callback_data="edit_subject")],
            [InlineKeyboardButton(text="👥 Номер группы", callback_data="edit_group_number")],
            [InlineKeyboardButton(text="👤 Номер подгруппы", callback_data="edit_subgroup_number")],
            [InlineKeyboardButton(text="📝 Регламент", callback_data="edit_regulation")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_settings")],
        ]
    )


@router.callback_query(SettingsStates.menu, F.data == "edit_teacher")
async def start_edit_teacher(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите ФИО преподавателя:\n"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="teacher")
    await state.set_state(SettingsStates.teacher)

@router.callback_query(SettingsStates.menu, F.data == "edit_teacher_email")
async def start_edit_teacher_email(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите новый контакт преподавателя "
        "(ник в Telegram, почта или номер телефона)"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="teacher_email")
    await state.set_state(SettingsStates.teacher_email)

@router.callback_query(SettingsStates.menu, F.data == "edit_subject")
async def start_edit_subject(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите новое название предмета:"
    )

    await state.update_data(last_bot_message_id=msg.message_id, edit_field="subject")
    await state.set_state(SettingsStates.subject)

@router.callback_query(SettingsStates.menu, F.data == "edit_group_number")
async def start_edit_group_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите новый номер группы"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="group_number")
    await state.set_state(SettingsStates.group_number)

@router.callback_query(SettingsStates.menu, F.data == "edit_subgroup_number")
async def start_edit_subgroup_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите новый номер подгруппы"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="subgroup_number")
    await state.set_state(SettingsStates.subgroup_number)

@router.callback_query(SettingsStates.menu, F.data == "edit_regulation")
async def start_edit_regulation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    msg = await callback.message.answer(
        "Введите новую ссылку на регламент"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="regulation_link")
    await state.set_state(SettingsStates.regulation_link)

@router.callback_query(SettingsStates.menu, F.data == "cancel_settings")
async def settings_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.clear()