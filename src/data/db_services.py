import asyncio
import logging
from typing import Sequence, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result, delete, update

from src.data.database import async_session, Base, get_db
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




@db_action
async def get_all_admins(session: AsyncSession):
    all_admins = await session.execute(
        select(
            User
        )
        .where(
            User.is_admin.is_(True)
        )
    )
    return all_admins.scalars().all()


@db_action
async def create_user(session: AsyncSession, **kwargs):
    session.add(kwargs.get('user'))


@db_action
async def get_user(session: AsyncSession, **kwargs):
    username: str = kwargs.get('username')

    user = await session.execute(
        select(
            User
        ).where(
            User.username == username
        )
    )
    return user.scalars().first()


@db_action
async def delete_admin(session: AsyncSession, **kwargs):
    username: str = kwargs.get('username')

    await session.execute(
        update(
            User
        ).where(
            User.username == username
        ).values(
            is_admin=False
        ))


@db_action
async def add_admin(session: AsyncSession, **kwargs):
    username: str = kwargs.get('username')

    await session.execute(
        update(
            User
        ).where(
            User.username == username
        ).values(
            is_admin=True
        )
    )

@db_action
async def update_user(session: AsyncSession, **kwargs):
    username: str = kwargs.get('username')
    updated_data = kwargs.get('updated_data')
    await session.execute(
        update(
            User
        ).where(
            User.username == username
        ).values(
            **updated_data
        )
    )

async def create_or_update_v2(**kwargs):
    username = kwargs.get('username')
    updated_data = kwargs.get('updated_data')

    user = await get_user(username=username, updated_data=updated_data)
    if user:
        await update_user(
            username=username,
            updated_data=dict(
            ))
    else:
        await create_user(
            user=updated_data
        )

# async def main():
#    await add_admin(username='nariman079i')
#
# asyncio.run(main())
