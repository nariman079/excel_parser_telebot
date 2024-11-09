from aiogram.filters import Filter
from aiogram.types import Message

from src.config import async_session
from src.data.sqlalchemy_ext import session_context
from src.services.v3.user_services import get_user


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        async with async_session.begin() as session:
            session_context.set(session)
            user = await get_user(message.from_user)
            if not user:
                return False
            elif user.is_admin:
                return True
            return False
