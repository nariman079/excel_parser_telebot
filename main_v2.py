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
from src.data.db_services import get_user
from src.services_v2.base_services import AddExcelFile, SingleAction, GetInstallmentPlanData, ShowInstallmentDetail, \
    CreateAdminUser, DeleteAdminUser, StartHandler, search_my_installment_plan
from src.state_groups import ExcelFileState, SearchInstallmentPlanState, CreateAdminUserState, GetContactUser

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')


async def get_start(
        message: Message,
        state: FSMContext
) -> None:
    await StartHandler.get_or_create_user(message, state)


async def get_main_menu(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        text="Вы вернулись в главное меню",
        reply_markup=await get_full_menu_markup(message.chat.username)
    )


async def get_my_installment_plans(
        message: Message,
        state: FSMContext
) -> None:
    await search_my_installment_plan(message)


async def get_back(
        message: Message,
        state: FSMContext
):
    await state.clear()
    await message.answer(
        text="Вы отменили действие",
        reply_markup=await get_full_menu_markup(message.chat.username)
    )


async def get_excel_file(
        message: Message,
        state: FSMContext
) -> None:
    user = await get_user(username=message.chat.username)
    if user and user.is_admin:
        await AddExcelFile().start(message, state)


async def get_installment_plan(
        message: Message,
        state: FSMContext
) -> None:
    user = await get_user(username=message.chat.username)
    if user and user.is_admin:
        await GetInstallmentPlanData.start(message, state)


async def callback_handler(callback: CallbackQuery):
    print(callback.data)
    if 'product_' in callback.data:
        await ShowInstallmentDetail(
            message=callback.message,
            product_number=int(callback.data.replace('product_', ''))
        ).execute()

    elif 'delete-' in callback.data:
        await callback.message.delete()
        await DeleteAdminUser.delete_admin(
            username=callback.data.split('-')[-1],
            message=callback.message
        )
    elif 'cancelled' in callback.data:
        await callback.message.delete()
        await callback.message.answer(
            text="Вы отменили удаление!",
            reply_markup=await get_full_menu_markup(callback.message.chat.username)
        )


async def create_admin_user(
        message: Message,
        state: FSMContext
) -> None:
    user = await get_user(username=message.chat.username)
    if user and user.is_admin:
        await CreateAdminUser.start(message, state)


async def start():
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))

    dp = Dispatcher()

    dp.message.register(
        get_start,
        CommandStart()
    )

    dp.message.register(
        get_main_menu,
        F.text == ButtonText.main_menu_button_text
    )
    # dp.message.register(
    #     get_back,
    #     F.text == ButtonText.back_button_text
    # )
    dp.message.register(
        get_excel_file,
        F.text == ButtonText.add_excel_file,
    )
    dp.message.register(
        AddExcelFile.get_and_check_file,
        ExcelFileState.file
    )
    dp.message.register(
        SingleAction.make_payment,
        F.text == ButtonText.make_payment_button_text
    )
    dp.message.register(
        SingleAction.send_application,
        F.text == ButtonText.send_application_button_text
    )
    dp.message.register(
        get_installment_plan,
        F.text == ButtonText.get_installment_plan_data_button_text
    )
    dp.message.register(
        GetInstallmentPlanData.get_search_method,
        SearchInstallmentPlanState.search_type
    )
    dp.message.register(
        GetInstallmentPlanData.search_by_phone_number,
        SearchInstallmentPlanState.phone_number
    )
    dp.message.register(
        GetInstallmentPlanData.search_by_number,
        SearchInstallmentPlanState.number
    )
    dp.message.register(
        create_admin_user,
        F.text == ButtonText.add_admin_button_text
    )
    dp.message.register(
        CreateAdminUser.get_username,
        CreateAdminUserState.username
    )
    dp.message.register(
        StartHandler.get_phone_number,
        GetContactUser.phone_number
    )
    dp.message.register(
        get_my_installment_plans,
        F.text == ButtonText.my_installment_plans
    )
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
