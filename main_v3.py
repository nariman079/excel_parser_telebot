import os
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram import F

from dotenv import load_dotenv

from src.buttons.main_buttons import ButtonText
from src.services.v3.command_services import start_handler, get_phone_number_handler, create_admin_handler, \
    get_admin_username_handler, cancelled_delete_admin_user_handler, delete_admin_handler
from src.state_groups import CreateAdminUserState, ExcelFileState, SearchInstallmentPlanState

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))

dp = Dispatcher()


@dp.message(CommandStart())
async def get_start(
        message: Message,
) -> None:
    """Запуск бота"""
    await start_handler(message)


@dp.message(F.text == ButtonText.main_menu_button_text)
async def get_main_menu_command(message: Message) -> None:
    """Главное меню"""
    pass


@dp.message(F.text == ButtonText.add_excel_file)
async def update_excel_file_command(
        message: Message,
        state: FSMContext
) -> None:
    """Обновление базы договоров"""
    pass


@dp.chat_member(ExcelFileState.file)
async def get_update_excel_file_command(
        message: Message,
        state: FSMContext
) -> None:
    """Получение файла при обновлении базы договоров"""
    pass


@dp.message(F.contact)
async def phone_request_command(
        message: Message,
) -> None:
    """Получение номера"""
    await get_phone_number_handler(message)


@dp.message(F.text == ButtonText.my_installment_plans)
async def get_my_installment_plans_command(message: Message) -> None:
    """Получение моих рассрочек"""
    pass


@dp.message(F.text == ButtonText.add_admin_button_text)
async def create_admin_command(
        message: Message,
        state: FSMContext
):
    """Создание админа"""
    await create_admin_handler(message, state)


@dp.message(CreateAdminUserState.username)
async def get_admin_username_command(
        message: Message,
        state: FSMContext
) -> None:
    """
    Получение имени пользователя при создании админа
    """
    await get_admin_username_handler(message, state)


@dp.message(F.text == ButtonText.make_payment_button_text)
async def make_payment_command(message: Message) -> None:
    """Совершение оплаты"""
    pass


@dp.message(F.text == ButtonText.send_application_button_text)
async def send_application_command(message: Message) -> None:
    """Отправка заявки"""
    pass


@dp.message(F.text == ButtonText.get_installment_plan_data_button_text)
async def get_installment_plan_data_command(
        message: Message,
        state: FSMContext
) -> None:
    """Получение данных о рассрочке"""
    pass


@dp.message(SearchInstallmentPlanState.search_type)
async def get_search_method_command(
        message: Message,
        state: FSMContext
) -> None:
    """Выбор метода поиска данных о рассрочке"""
    pass


@dp.message(SearchInstallmentPlanState.phone_number)
async def search_by_phone_number_command(
        message: Message,
        state: FSMContext
) -> None:
    """Поиск по номеру телефона данных о рассрочке"""
    pass


@dp.message(SearchInstallmentPlanState.number)
async def get_search_by_number_command(
        message: Message,
        state: FSMContext
) -> None:
    """Поиск по номеру договора"""
    pass


async def callback_handler(callback: CallbackQuery):
    # my_user = await get_user(callback.from_user)

    if 'product_' in callback.data:
        ...
        # await ShowInstallmentDetail(
        #     message=callback.message,
        #     product_number=int(callback.data.replace('product_', ''))
        # ).execute()

    elif 'delete-' in callback.data:
        await delete_admin_handler(callback)
    elif 'cancelled' in callback.data:
        await cancelled_delete_admin_user_handler(callback)


async def start():
    dp.callback_query.register(
        callback_handler,
        lambda call: call.data
    )
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
