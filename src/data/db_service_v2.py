import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.data.database import async_session
from src.data.models import User


def db_action(func):
    """ Декоратор """

    async def wrapper(**kwargs):
        try:
            async with async_session() as session:
                async with session.begin():
                    return await func(session, **kwargs)
        except Exception as error:
            logging.log(
                level=logging.ERROR,
                msg="\n".join(error.args)
            )

    return wrapper


class UserDB:
    def __init__(self, telegram_id: str):
        self.telegram_id = telegram_id

    async def get_user(self) -> User | None:
        try:
            async with async_session() as session:
                async with session.begin():
                    all_admins = await session.query(User).filter(
                            User.telegram_id == self.telegram_id)
                    return all_admins.scalars().first()
        except Exception as error:
            logging.log(
                level=logging.ERROR,
                msg="\n".join(error.args)
            )
            return None

    async def update_user(self, new_user: User) -> User:
        try:
            async with async_session() as session:
                async with session.begin():
                    new_user = await session.execute(
                        update(User).where(
                            User.telegram_id == self.telegram_id
                        ).values(new_user)
                    )
                    return new_user
        except Exception as error:
            logging.log(
                level=logging.ERROR,
                msg="\n".join(error.args)
            )
            return None

    @staticmethod
    async def create_user(user: User):
        try:
            async with async_session() as session:
                async with session.begin():
                    session.add(user)
                    return user
        except Exception as error:
            logging.log(
                level=logging.ERROR,
                msg="\n".join(error.args)
            )
            return None

