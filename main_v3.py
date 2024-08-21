import os
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram import F

from src.buttons_v2 import get_full_menu_markup, ButtonText
from src.services.v3.command_services import start_handler, get_phone_number_handler
from src.state_groups import GetContactUser

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))

dp = Dispatcher()


@dp.message(CommandStart())
async def get_start(
        message: Message,
) -> None:
    await start_handler(message)


@dp.message(F.contact)
async def phone_request_command(
        message: Message,
):
    await get_phone_number_handler(message)


async def start():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
