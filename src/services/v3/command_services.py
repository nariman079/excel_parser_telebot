from aiogram.types import Message

from src.services.v3.base_services import generate_message_args
from src.services.v3.user_services import get_user, create_or_update_user, get_custom_user


async def start_handler(message: Message):
    """Обработчик команды /start"""
    tg_user = message.from_user
    db_user = await get_user(tg_user)
    message_args = await generate_message_args(db_user)

    await message.answer(
        **message_args
    )


async def get_phone_number_handler(
        message: Message,
):
    custom_user = await get_custom_user(
        tg_user=message.from_user,
        phone_number=message.contact.phone_number
    )
    db_user_data = await create_or_update_user(custom_user)
    message_args = await generate_message_args(db_user_data)

    await message.answer(
        **message_args
    )
