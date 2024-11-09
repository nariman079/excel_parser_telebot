from collections import namedtuple

from aiogram.types import User as TgUser
from sqlalchemy.testing.plugin.plugin_base import logging
import logging
from src.data.models import User


async def generate_user_data(tg_user: TgUser) -> dict:
    user_data = dict(
        telegram_id=tg_user.id,
        username=tg_user.username,
        phone_number=tg_user.phone_number
    )
    return user_data


async def get_user(
        tg_user: TgUser | None = None,
        chat_id: int | str | None = None) -> User:
    if chat_id:
        user = await User.find_first_by_kwargs(telegram_id=chat_id)
        return user
    if tg_user.username:
        user = await User.find_first_by_kwargs(username=tg_user.username)
        return user
    user = await User.find_first_by_kwargs(telegram_id=tg_user.id)
    return user


async def get_admin_user(username: str) -> User:
    return await User.find_first_by_kwargs(username=username)


async def get_user_data(tg_user: TgUser) -> dict:
    return await generate_user_data(tg_user)


async def create_or_update_user(tg_user: User):
    user_data = await get_user_data(tg_user)
    db_user = await get_user(tg_user)
    if db_user:
        logging.info(f"Update data, {user_data}")
        db_user.update(**user_data)
        return db_user
    else:
        logging.info(f"Create data, {user_data}")
        return await User.create(**user_data)


async def delete_admin_user(username: str):
    admin_user =await User.find_first_by_kwargs(username=username)
    admin_user.update(is_admin=False)

    return admin_user


async def create_admin_user(username: str):
    admin_user = await User.create(
        username=username,
        is_admin=True
    )
    return admin_user

async def set_admin_user(username: str):
    admin_user = await User.find_first_by_kwargs(
        username=username
    )
    admin_user.update(is_admin=True)
    return admin_user


async def get_custom_user(tg_user: TgUser, **kwargs):
    CustomUser = namedtuple(
        'User',
        [
            'id',
            'username',
            'phone_number'
        ]
    )
    custom_user = CustomUser(
        id=tg_user.id,
        username=tg_user.username,
        **kwargs
    )
    return custom_user



