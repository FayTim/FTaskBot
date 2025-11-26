import re

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command
from src.db.database import async_session_factory
from src.app.delete_msg import delete_last_bot_message
from src.app.states import SettingsStates

router = Router(name="settings")
settings = {}
@router.message(Command('settings'))
async def get_settings(message : Message, state : FSMContext):

    msg = await message.answer("Привет👋 \n"
                                   "Добро пожаловать в настройки бота \n"
                                   "Для начала давай впишем ФИО преподавателя")

    await state.set_state(SettingsStates.teacher)
    await state.update_data(last_bot_message_id=msg.message_id)
    await message.delete()
    print(f"[FSM] Текущее состояние: {await state.get_state()}\n")

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

    await state.update_data(teacher=teacher)
    await delete_last_bot_message(message, state)

    msg = await message.answer("Давай также впишем контакт преподавателя (это может быть ник в телеграмм или почта, или что-то еще)")

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

    await state.update_data(teacher_email=email)
    await delete_last_bot_message(message, state)

    msg = await message.answer("Хорошо, теперь впишем название предмета, который вы изучаете")

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.subject)
    await message.delete()

    print(f"[FSM] state={await state.get_state()} data={await state.get_data()}\n")

@router.message(F.text, SettingsStates.subject)
async def get_subject(message: Message, state: FSMContext):
    subject = message.text.strip()
    if not re.fullmatch(r'[А-ЯЁа-яё]+', subject):
        msg = await message.answer("Что не так написано в предмете\n"
                                   f"Ваш ввод: {subject}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    await state.update_data(subject=subject)
    await delete_last_bot_message(message, state)

    msg = await message.answer("Впишите номер студенческой группы в сокращенном виде (ФТ-101, ФТ-204)")

    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.group_number)
    await message.delete()
    print(f"[FSM] state={await state.get_state()} data={await state.get_data()}\n")


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

    await state.update_data(group_number=group)

    await delete_last_bot_message(message, state)

    msg = await message.answer("Впишите номер подгруппы для которой предназначен этот предмет"
                         "Если для всей группы введите просто 0 😊")
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.subgroup_number)
    await message.delete()

@router.message(F.text, SettingsStates.subgroup_number)
async def get_group_number(message: Message, state: FSMContext):
    subgroup = message.text.strip()
    if not re.fullmatch('[0-2]', subgroup):
        msg = await message.answer("Что не так в номере вашей подгруппы(\n"
                                   f"Ваш ввод: {subgroup}\n"
                                   f"Попробуйте снова")
        await delete_last_bot_message(message, state)
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()
        return

    await state.update_data(subgroup_number=subgroup)

    await delete_last_bot_message(message, state)
    chat_id = message.chat.id
    settings[chat_id] = await state.get_data()
    print(settings)
    async with async_session_factory as session:
        # await save_chat_settings(chat_id=chat_id, data=data, session=session)
        await session.commit()
    msg = await message.answer("Спасибо! Настройки завершены 😊")
    await state.update_data(last_bot_message_id=msg.message_id)
    await state.set_state(SettingsStates.subgroup_number)
    await message.delete()


    # print(f"[FSM] state={await state.get_state()} data={await state.get_data()}\n")

