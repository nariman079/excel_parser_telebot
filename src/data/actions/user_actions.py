import logging

from aiogram.types import User as TgUser
from sqlalchemy import select, update

from src.data.database import async_session
from src.data.models import User


async def get_user_from_db(
        field_name: str,
        tg_user: TgUser
) -> User | None:
    """Получение пользователя из базы данных"""
    try:
        async with async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(
                        User
                    ).where(
                        getattr(User, field_name) == str(tg_user.id)
                    )
                )
                return query.scalars().first()
    except Exception as error:
        logging.log(
            level=logging.ERROR,
            msg="\n".join(error.args)
        )
        return None


async def create_user_on_db(
        new_user: User
) -> User | None:
    """Создание пользователя в базе данных"""
    try:
        async with async_session() as session:
            async with session.begin():
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
    except Exception as error:
        logging.log(
            level=logging.ERROR,
            msg="\n".join(error.args)
        )
        return None


async def update_user_on_db(
        user_id: int,
        new_user: User
) -> User | None:
    """Изменение пользователя в базе данных"""
    try:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(
                        User
                    ).where(
                        User.id == user_id
                    ).values(
                        is_admin=new_user.is_admin,
                        phone_number=new_user.phone_number,
                    )
                )
                await session.commit()
                return new_user
    except Exception as error:
        logging.log(
            level=logging.ERROR,
            msg="\n".join(error.args)
        )
        return None
