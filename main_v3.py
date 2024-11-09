import logging
import os
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram import F

from dotenv import load_dotenv


from src.buttons.main_buttons import ButtonText
from src.filters import AdminFilter
from src.middlewares import SessionMiddleware
from src.services.v3.command_services import start_handler, get_phone_number_handler, create_admin_handler, \
    get_admin_username_handler, cancelled_delete_admin_user_handler, delete_admin_handler, make_payment_handler, \
    send_application_handler, show_installment_detail_callback_handler, get_installment_plan_data_handler, \
    get_search_type_handler, get_main_menu_handler, get_search_by_number_handler, get_my_installment_plans, \
    search_by_phone_number_handler, get_excel_file_command, add_excel_file_command
from src.state_groups import CreateAdminUserState, ExcelFileState, SearchInstallmentPlanState, GetContactUser

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')


bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True
    )
)

admin_router = Router()
custom_user_router = Router()
admin_router.message.filter(AdminFilter())

dp = Dispatcher()


@dp.message(CommandStart())
async def get_start(
        message: Message,

) -> None:
    """Запуск бота"""
    await start_handler(message)


@dp.message(F.text == ButtonText.main_menu_button_text)
async def get_main_menu_command(
        message: Message,
        state: FSMContext
) -> None:
    """Главное меню"""
    await get_main_menu_handler(
        message, state
    )



@dp.message(F.contact)
async def phone_request_command(
        message: Message,
        state: FSMContext
) -> None:
    """Получение номера"""
    await get_phone_number_handler(message)


@custom_user_router.message(F.text == ButtonText.my_installment_plans)
async def get_my_installment_plans_command(message: Message) -> None:
    """Получение моих рассрочек"""
    await get_my_installment_plans(message)


@admin_router.message(F.text == ButtonText.add_admin_button_text)
async def create_admin_command(
        message: Message,
        state: FSMContext
):
    """Создание админа"""
    await create_admin_handler(message, state)

@admin_router.message(CreateAdminUserState.username)
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
    await make_payment_handler(message)


@dp.message(F.text == ButtonText.send_application_button_text)
async def send_application_command(message: Message) -> None:
    """Отправка заявки"""
    await send_application_handler(message)


@admin_router.message(F.text == ButtonText.get_installment_plan_data_button_text)
async def get_installment_plan_data_command(
        message: Message,
        state: FSMContext
) -> None:
    """Получение данных о рассрочке"""
    await get_installment_plan_data_handler(
        message, state
    )


@admin_router.message(F.text == ButtonText.add_excel_file)
async def add_excel_file(message: Message, state: FSMContext):
    """Добавление файла Excel"""
    await add_excel_file_command(message, state)



@admin_router.message(SearchInstallmentPlanState.search_type)
async def select_search_method_command(
        message: Message,
        state: FSMContext
) -> None:
    """Выбор метода поиска данных о рассрочке"""
    await get_search_type_handler(
        message, state
    )


@admin_router.message(SearchInstallmentPlanState.phone_number)
async def search_by_phone_number_command(
        message: Message,
        state: FSMContext
) -> None:
    """Поиск по номеру телефона данных о рассрочке"""
    await search_by_phone_number_handler(message, state)

@admin_router.message(SearchInstallmentPlanState.number)
async def get_search_by_number_command(
        message: Message,
        state: FSMContext
) -> None:
    """Поиск по номеру договора"""
    await get_search_by_number_handler(
        message, state
    )

@admin_router.message(ExcelFileState.file)
async def get_excel_file(message: Message, state: FSMContext):
    """Обработка Excel файла"""
    await get_excel_file_command(message, state)

async def callback_handler(callback: CallbackQuery):
    if 'product-' in callback.data:
        await show_installment_detail_callback_handler(callback)
    elif 'delete-' in callback.data:
        await delete_admin_handler(callback)
    elif 'cancelled' in callback.data:
        await cancelled_delete_admin_user_handler(callback)


async def start():

    dp.include_routers(custom_user_router, admin_router)
    dp.callback_query.register(
        callback_handler,
        lambda call: call.data
    )
    dp.callback_query.middleware.register(SessionMiddleware())

    dp.message.middleware.register(SessionMiddleware())

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(start())
