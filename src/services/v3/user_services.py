from collections import namedtuple

from aiogram.types import User as TgUser

from src.data.actions.user_actions import get_user_from_db, create_user_on_db, update_user_on_db, update_user_field
from src.data.models import User


async def generate_user_data(tg_user: TgUser) -> User:
    db_user = User(
        telegram_id=tg_user.id,
        username=tg_user.username,
        phone_number=tg_user.phone_number
    )
    return db_user


async def get_user(tg_user: TgUser) -> User:
    return await get_user_from_db(
        'telegram_id',
        tg_user,
        'id'
    )


async def get_admin_user(tg_user: TgUser) -> User:
    return await get_user_from_db(
        'username',
        tg_user,
        'username'
    )


async def get_user_data(tg_user: TgUser) -> User:
    return await generate_user_data(tg_user)


async def create_or_update_user(tg_user: User):

    user_data = await get_user_data(tg_user)
    db_user = await get_user(tg_user)

    if db_user:
        return await update_user_on_db(
            db_user.id,
            user_data
        )
    else:
        return await create_user_on_db(user_data)


async def delete_admin_user(username: str):
    return await update_user_field(username)


async def create_admin_user(username: str):
    admin_user = User(
        username=username,
        is_admin=True
    )
    return await create_user_on_db(admin_user)


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


async def generate_admin_user(username: str):
    AdminUser = namedtuple(
        'User',
        [
            'username',
        ]
    )
    admin_user = AdminUser(
        username=username,
    )
    return admin_user
