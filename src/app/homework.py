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
    # await state.set_state(HomeworkStates.subject)
    # keyboard = await kb.inline_subjects()
    # msg = await message.answer(
    #     "Введите информацию по заданию:\nСначала выберите предмет",
    #     reply_markup=keyboard
    # )
    # await state.update_data(last_bot_message_id=msg.message_id)
    # await message.delete()
    data = await state.get_data()
    subject = data["subject"]
    hw = Homework(subject=subject)
    await state.update_data(homework=hw.to_dict())
    await state.set_state(HomeworkStates.homework_data)

    msg = await message.answer('Отправьте текст задания, фото, ссылку или pdf')

    await state.update_data(last_bot_message_id=msg.message_id)
    await message.delete()

# @router.callback_query(HomeworkStates.subject)
# async def get_homework_data(callback : CallbackQuery, state : FSMContext):
#
#     hw = Homework(subject=next(k for k,v in kb.subjects.items() if v == callback.data))
#     print(hw)
#
#     await callback.answer()
#     await state.update_data(homework=hw.to_dict())
#     await state.set_state(HomeworkStates.homework_data)
#
#     msg = await callback.message.edit_text('Отправьте текст задания, фото, ссылку или pdf')
#     await state.update_data(last_bot_message_id=msg.message_id)

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

@router.message(HomeworkStates.homework_data, F.document)
async def get_doc(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)

    data = await state.get_data()
    hw = Homework(**data.get("homework_data"))
    hw.document = message.document.file_id

    await state.update_data(homework=hw.to_dict())
    await state.set_state(HomeworkStates.deadline)

    msg = await message.answer("Напишите дедлайн задания в формате: hh:mm dd.mm.yy")
    await state.update_data(last_bot_message_id=msg.message_id)

    await message.delete()

@router.message(lambda m: not m.media_group_id, HomeworkStates.homework_data, F.photo)
async def get_photo(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)
    await message.delete()

    data = await state.get_data()
    hw = Homework(**data.get("homework_data"))
    hw.media.append(message.photo[-1].file_id)

    await state.update_data(homework=hw.to_dict())
    await state.set_state(HomeworkStates.deadline)

    msg = await message.answer("Напишите дедлайн задания в формате: hh:mm dd.mm.yy")
    await state.update_data(last_bot_message_id=msg.message_id)


@router.message(lambda m: m.media_group_id, HomeworkStates.homework_data, F.photo)
async def get_media(message : Message, state : FSMContext):
    await delete_last_bot_message(message, state)

    group_id = message.media_group_id
    if group_id not in media_groups_temp:
        media_groups_temp[group_id] = []
    file_id = message.photo[-1].file_id
    media_groups_temp[group_id].append(file_id)

    await asyncio.sleep(MEDIA_GROUP_TIMEOUT)
    group_files = media_groups_temp.pop(group_id, None)

    if group_files:
        data = await state.get_data()
        hw = Homework(**data.get("homework_data"))
        hw.media.extend(group_files)
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
            f"Документов: {1 if hw.document else 0}\n"
            f"Фото: {len(hw.media)}\n"
            f"Дедлайн: {hw.deadline}\n\n"
        )
        await state.update_data(last_bot_message_id=None)
        await message.delete()
    except Exception:
        msg = await message.answer("Что-то не то с дедлайном(")
        await state.update_data(last_bot_message_id=msg.message_id)
        await message.delete()