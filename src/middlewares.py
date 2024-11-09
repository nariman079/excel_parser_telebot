from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.config import async_session
from src.data.sqlalchemy_ext import session_context


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        async with async_session.begin() as session:
            token = session_context.set(session)
            try:
                return await handler(event, data)
            finally:
                session_context.reset(token)