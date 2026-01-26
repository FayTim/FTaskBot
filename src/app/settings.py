import re

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from src.app.delete_msg import delete_last_bot_message
from src.app.states import SettingsStates
from src.app.subjects import find_subject

from src.db.metods_db_settings import *

router = Router(name="settings")
settings = None
@router.message(Command('settings'))
async def get_settings(message : Message, state : FSMContext):
    chat_id = message.chat.id
    if await get_settings_chat(chat_id) is None:
        msg = await message.answer("Привет👋 \n"
                                   "Добро пожаловать в настройки бота \n"
                                   "Для начала, давай впишем название предмета, который вы изучаете",
                                   reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_settings")],
                ])
        )

        await state.set_state(SettingsStates.subject)
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await message.delete()
    else:
        msg = await message.answer("Настройки для этого чата уже есть\n"
                                   "Что вы хотите изменить?",
                                   reply_markup=settings_menu_kb())
        await state.set_state(SettingsStates.menu)
        await state.update_data(last_bot_message_id=msg.message_id, edit_field=None)
        await message.delete()

@router.message(F.text, SettingsStates.subject)
async def get_subject(message: Message, state: FSMContext):
    subject = message.text.strip()
    if not re.fullmatch(r'[А-ЯЁа-яёA-Za-z+# ]+', subject):
        msg = await message.answer("Что не так написано в предмете\n"
                                   f"Ваш ввод: {subject}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    data = await state.get_data()
    edit_field = data.get("edit_field")
    check_subject = find_subject(subject)

    if len(check_subject) > 0:
        subject = check_subject

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
        msg = await message.answer("Впишите номер подгруппы для которой предназначен этот предмет \n"
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
        data = await state.get_data()
        subject_name = data.get("subject")
        int_group_number = int(data.get("group_number").split("-")[1])
        int_subgroup_number = int(data.get("subgroup_number"))
        possible_settings = await check_db_exist_course(subject_name, int_group_number, int_subgroup_number)
        if possible_settings is None:
            msg = await message.answer("Давай теперь впишем ФИО преподавателя \n"
                                       "P.S. если не знаете отчество, введите только фамилию и имя")
            await state.update_data(last_bot_message_id=msg.message_id)
            await state.set_state(SettingsStates.teacher)
            await message.delete()
        else:
            name_teacher, email_teacher, regulation_link = possible_settings
            await state.update_data(teacher=name_teacher)
            await state.update_data(teacher_email=email_teacher)
            await state.update_data(regulation_link=regulation_link)
            msg = await message.answer("Это случайно не то что ты ищешь? \n"
                                       "КУРС:\n"
                                       f"Предмет📚: {subject_name}\n"
                                       f"Для группы👥: ФТ-{int_group_number}{"-"+str(int_subgroup_number) if int_subgroup_number != 0 else ""}\n"
                                       f"Преподаватель👨‍🏫: {name_teacher}\n"
                                       f"Контакт преподавателя📧: {email_teacher}\n"
                                       f"Регламент📝: {regulation_link}",
                                       reply_markup=setting_exist_db())
            await delete_last_bot_message(message, state)
            await state.update_data(last_bot_message_id=msg.message_id)
            await message.delete()


@router.callback_query(SettingsStates.subgroup_number, F.data == "course_exist")
async def course_exist_db(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    chat_id = callback.message.chat.id
    await update_chat_settings(chat_id, data)

    msg = await callback.message.answer("Спасибо! Настройки завершены 😊")
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.clear()
    await callback.message.delete()

@router.callback_query(SettingsStates.subgroup_number, F.data == "course_not_exist")
async def course_not_exist_db(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(
        teacher=None,
        teacher_email=None,
        regulation_link=None
    )
    msg = await callback.message.answer("Понял! Давай теперь впишем ФИО преподавателя👨‍🏫 \n"
                                        "P.S. если не знаете отчество, введите только фамилию и имя")
    await delete_last_bot_message(callback.message, state)
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.teacher)

@router.message(F.text, SettingsStates.teacher)
async def get_teacher(message : Message, state : FSMContext):
    teacher = message.text.strip()
    if not (re.fullmatch(r'([А-ЯЁа-яё]+) ([А-ЯЁа-яё]+) ([А-ЯЁа-яё]+)', teacher)\
            or re.fullmatch(r'([А-ЯЁа-яё]+) ([А-ЯЁа-яё]+)', teacher)):
        msg = await message.answer("Что-то не то с вводом ФИО преподавателя(\n"
                                   f"Ваш ввод: {teacher}\n"
                                   "Введите пожалуйста ещё раз")
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
        await update_teacher_in_db(chat_id, new_teacher_name=teacher)

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
        await update_teacher_email_in_db(chat_id, email)
        msg = await message.answer("Контакт преподавателя обновлен ✅")
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

def setting_exist_db() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да! Это мой курс", callback_data="course_exist")],
            [InlineKeyboardButton(text="Нет! Это не мой курс", callback_data="course_not_exist")]
        ]
    )
@router.callback_query(SettingsStates.menu, F.data == "edit_teacher")
async def start_edit_teacher(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)
    settings = await get_settings_chat(callback.message.chat.id)
    data_teacher = await get_teacher_by_id(settings.teacher_id)
    current_teacher = data_teacher.name_teacher
    msg = await callback.message.answer(
        f"Текущие данные о преподавателе: {current_teacher} \n"
        "Введите новые данные о преподавателе:\n"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="teacher")
    await state.set_state(SettingsStates.teacher)

@router.callback_query(SettingsStates.menu, F.data == "edit_teacher_email")
async def start_edit_teacher_email(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    settings = await get_settings_chat(callback.message.chat.id)
    data_teacher = await get_teacher_by_id(settings.teacher_id)
    current_teacher_email = data_teacher.email_teacher
    msg = await callback.message.answer(
        f"Текущие данные о связи с преподавателем: {current_teacher_email}\n"
        "Введите новый контакт преподавателя "
        "(ник в Telegram, почта или номер телефона)"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="teacher_email")
    await state.set_state(SettingsStates.teacher_email)

@router.callback_query(SettingsStates.menu, F.data == "edit_subject")
async def start_edit_subject(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    settings = await get_settings_chat(callback.message.chat.id)
    current_subject_name = settings.subject_name
    msg = await callback.message.answer(
        f"Текущее название предмета: {current_subject_name}\n"
        "Введите новое название предмета:"
    )

    await state.update_data(last_bot_message_id=msg.message_id, edit_field="subject")
    await state.set_state(SettingsStates.subject)

@router.callback_query(SettingsStates.menu, F.data == "edit_group_number")
async def start_edit_group_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    settings = await get_settings_chat(callback.message.chat.id)
    data_group_number = await get_group_by_id(settings.group_id)
    current_group_number = data_group_number.group_number
    msg = await callback.message.answer(
        f"Текущие данные о номере группы: {current_group_number}\n"
        "Введите новый номер группы"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="group_number")
    await state.set_state(SettingsStates.group_number)

@router.callback_query(SettingsStates.menu, F.data == "edit_subgroup_number")
async def start_edit_subgroup_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)

    settings = await get_settings_chat(callback.message.chat.id)
    data_subgroup_number = await get_group_by_id(settings.group_id)
    current_subgroup_number = data_subgroup_number.subgroup_number
    msg = await callback.message.answer(
        f"Текущие данные о номере подгруппы: {current_subgroup_number}\n"
        "Введите новый номер подгруппы"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="subgroup_number")
    await state.set_state(SettingsStates.subgroup_number)

@router.callback_query(SettingsStates.menu, F.data == "edit_regulation")
async def start_edit_regulation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await delete_last_bot_message(callback.message, state)
    settings = await get_settings_chat(callback.message.chat.id)
    current_regulation_link = settings.regulation_link
    msg = await callback.message.answer(
        f"Текущие данные о ссылке на регламент: {current_regulation_link}\n"
        "Введите новую ссылку на регламент"
    )
    await state.update_data(last_bot_message_id=msg.message_id, edit_field="regulation_link")
    await state.set_state(SettingsStates.regulation_link)

@router.callback_query(SettingsStates.menu, F.data == "cancel_settings")
async def settings_back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await state.clear()