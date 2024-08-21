import asyncio


from sqlalchemy import update, select
from pydantic import BaseModel
from src.data.database import async_session
from src.data.models import User


class UserSchema(BaseModel):
    telegram_id: int
    username: str

async def update_user():
    new_user = UserSchema(
        telegram_id=12,
        username="23"
    )
    smt = select(User).where(User.telegram_id == 12)
    print(smt)
    # async with async_session() as session:
    #     async with session.begin():
    #         new_user = await session.execute(
    #
    #         )
    #         return new_user

asyncio.run(update_user())