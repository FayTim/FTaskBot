from aiogram.types import Message
from aiogram.fsm.context import FSMContext

async def delete_last_bot_message(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("last_bot_message_id")
    if msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception:
            pass