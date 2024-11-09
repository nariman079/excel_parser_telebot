import asyncio
import os

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from pandas import read_excel

from src.buttons.main_buttons import get_main_menu, get_user_menu, get_confirm_buttons, get_search_variant_buttons, \
    ButtonText, get_back_button, get_back_and_main_menu_button, generate_product_list_buttons, generate_restart_button
from src.buttons.main_buttons import get_search_buttons
from src.config import KEYS_FOR_GENERATE_MESSAGE
from src.services.exel_services import find_rows_by_phone_number_for_me, get_excel_data, find_rows_by_phone_number
from src.services.v3.base_services import generate_message_args, generate_single_action_message_args, \
    generate_installment_detail_message_args, generate_search_type_message_args
from src.services.v3.user_services import get_user, create_or_update_user, get_custom_user, get_admin_user, \
    create_admin_user, delete_admin_user, set_admin_user
from src.state_groups import CreateAdminUserState, SearchInstallmentPlanState, ExcelFileState

owner_admin = "RonnyKray"

async def base_show_installment_detail(
        product_number: str | int,
        message: Message,
) -> None:
    """"""
    user = await get_user(chat_id=message.chat.id)
    logging.info(f"User: {user.__dict__}")

    message_args = await generate_installment_detail_message_args(
        product_number,
        user
    )
    await message.answer(
        **message_args
    )


async def start_handler(message: Message) -> None:
    """Обработчик команды /start"""
    tg_user = message.from_user
    db_user = await get_user(tg_user)
    message_args = await generate_message_args(db_user)

    await message.answer(
        **message_args
    )


async def get_main_menu_handler(
        message: Message,
        state: FSMContext
) -> None:
    """Обработчик текста Главное меню"""
    user = await get_user(message.from_user)
    await message.answer(
        text="Вы вернулись на главное меню",
        reply_markup=await get_user_menu(user)
    )
    await state.clear()


async def get_phone_number_handler(
        message: Message,
) -> None:
    """Обработчик получения номера телефона"""
    custom_user = await get_custom_user(
        tg_user=message.from_user,
        phone_number=message.contact.phone_number
    )
    db_user_data = await create_or_update_user(custom_user)
    message_args = await generate_message_args(db_user_data)

    await message.answer(
        **message_args
    )



async def create_admin_handler(message: Message, state: FSMContext) -> None:
    """Обработчик создания админа"""
    await message.answer(
        text="Введите username пользователя с @:",
        reply_markup=await get_main_menu()
    )
    await state.set_state(CreateAdminUserState.username)


async def get_admin_username_handler(
        message: Message,
        state: FSMContext
) -> None:
    """Обработчик введенного имени пользователя при создании админа"""
    username = message.text
    my_user = await get_user(message.from_user)
    print("tesy")
    if '@' in username:
        username = username[1:]

    user = await get_admin_user(username=username)

    if not user:
        new_user = await create_admin_user(username)
        logging.info(f"Created new admin {new_user.username}")
        await message.answer(
            text=f"Администратор {username} успешно создан",
            reply_markup=await get_user_menu(my_user)
        )

    elif user and user.is_admin:
        await message.answer(
            text="Такой администратор уже есть в Базе данных, хотите удалить его?",
            reply_markup=await get_confirm_buttons(username)
        )
    elif user and not user.is_admin:
        logging.info(f"{user.username} appointed as an administrator")
        await set_admin_user(user.username)
        await message.answer(
            text=f"Пользователь @{username} назначен администратором",
            reply_markup=await get_user_menu(my_user)
        )
        if user.telegram_id:
            await message.bot.send_message(
                chat_id=user.telegram_id,
                text="Вы назначены администратором",
                reply_markup=await get_user_menu(user)
            )

    await state.clear()


async def cancelled_delete_admin_user_handler(callback: CallbackQuery):
    """ Обработчик отмены удаления """
    user = await get_user(callback.from_user)
    await callback.message.delete()
    await callback.message.answer(
        text="Вы отменили удаление!",
        reply_markup=await get_user_menu(user)
    )


async def delete_admin_handler(callback: CallbackQuery) -> None:
    message = callback.message
    username = callback.data.split('-')[-1]

    deleted_admin = await delete_admin_user(username)
    user = await get_user(chat_id=message.chat.id)
    await callback.message.delete()
    if deleted_admin:
        if deleted_admin.telegram_id:
            await message.bot.send_message(
                chat_id=deleted_admin.telegram_id,
                text="Вы больше не являетесь администратором",
                reply_markup=generate_restart_button()
            )
        await message.answer(
            text=f"Администратор {username} удален из системы",
            reply_markup=await get_user_menu(user)
        )
    else:
        await message.answer(
            text="Произошла ошибка, попробуйте чуть позже",
            reply_markup=await get_user_menu(user)
        )


async def make_payment_handler(message: Message) -> None:
    """Обработчик соверщения оплаты"""
    message_args = await generate_single_action_message_args(
        inline_text="Whatsapp",
        text="Нажмите чтобы перейти по ссылке:",
        inline_url="https://wa.me/message/SJ3CGLTME3CDP1"
    )

    await message.answer(
        **message_args
    )


async def send_application_handler(message: Message) -> None:
    """Обработчик отправки заявки"""

    message_args = await generate_single_action_message_args(
        inline_text="ansar05.ru",
        text="Нажмите чтобы перейти по ссылке:",
        inline_url="https://ansar05.ru/"
    )

    await message.answer(
        **message_args
    )


async def show_installment_detail_callback_handler(
        callback: CallbackQuery
) -> None:
    """
    Обработчик получения детальной
    информации о договоре
    """

    message = callback.message
    product_number = callback.data.split('-')[-1]
    logging.info(msg=f"Start proccess product {product_number}")
    await base_show_installment_detail(
        product_number=product_number,
        message=message
    )


async def get_installment_plan_data_handler(
        message: Message,
        state: FSMContext
) -> None:
    """Обработчик получения данных о рассрочке"""
    await message.answer(
        text="Выберите способ поиска:",
        reply_markup=await get_search_variant_buttons()
    )
    await state.set_state(SearchInstallmentPlanState.search_type)


async def get_search_type_handler(
        message: Message,
        state: FSMContext
) -> None:
    """Обработчик получения типа поиска"""

    user = await get_user(message.from_user)


    match message.text:
        case ButtonText.search_by_phone_number_button_text:
            message_args = await generate_search_type_message_args(
                text="Введите номер телефона:\nПример: 89280001288"
            )
            await message.answer(**message_args)
            await state.set_state(SearchInstallmentPlanState.phone_number)
        case ButtonText.search_by_number_button_text:
            message_args = await generate_search_type_message_args(
                text="Введите номер договора:\nПример: 324",
            )
            await message.answer(**message_args)
            await state.set_state(SearchInstallmentPlanState.number)
        case _:
            await message.answer(
                text="Выберите правильный способ поиска",
                reply_markup=await get_search_variant_buttons()
            )
            await state.set_state(SearchInstallmentPlanState.search_type)


async def search_by_phone_number_handler(
        message: Message, state: FSMContext
) -> None:
    """Обработчик поиска по номеру телефона данных о рассрочке"""
    user = await get_user(message.from_user)
    try:
        if message.text == ButtonText.back_button_text:
            await message.answer(
                text="Выберите способ поиска:",
                reply_markup=get_search_buttons()
            )
            await state.set_state(SearchInstallmentPlanState.search_type)
            return
        phone_number = message.text
        if not phone_number.isdigit():
            await message.answer(
                text="Попробуйте еще раз!\nВведите правильный номер телефона\nПример: 89280001288",
                reply_markup=await get_back_and_main_menu_button()
            )
            await state.set_state(SearchInstallmentPlanState.phone_number)
            return

    except Exception as error:
        await message.answer(
            text="Попробуйте еще раз!\nВведите правильный номер телефона\nПример: 89280001288",
            reply_markup=await get_back_and_main_menu_button()
        )
        await state.set_state(SearchInstallmentPlanState.phone_number)

        return
    await message.answer(
        text="Поиск по номеру телефона",
        reply_markup=None
    )
    excel_data = get_excel_data()

    searched_data = find_rows_by_phone_number(
        phone_number=phone_number,
        rows_list=excel_data
    )
    if len(searched_data) == 0:
        await message.answer(
            text="Такого номера телефона в договорах не найдено",
            reply_markup=await get_user_menu(user)
        )
        return

    await message.answer(
        text="Найденные рассрочки",
        reply_markup=generate_product_list_buttons(searched_data)
    )

    await state.clear()

async def get_search_by_number_handler(
        message: Message, state: FSMContext
) -> None:
    """Обработчик поиска по номеру договора"""
    try:
        if message.text == ButtonText.back_button_text:
            await message.answer(
                text="Выберите способ поиска:",
                reply_markup=await get_search_variant_buttons()
            )
            await state.set_state(SearchInstallmentPlanState.search_type)
            return
        number = message.text
        if not number.isdigit():
            await message.answer(
                text="Попробуйте еще раз!\nВведите правильный номер договора\nПример: 943",
                reply_markup=await get_back_and_main_menu_button()
            )
            await state.set_state(SearchInstallmentPlanState.number)
            return

    except Exception:
        await message.answer(
            text="Попробуйте еще раз!\nВведите правильный номер договора\nПример: 943",
            reply_markup=await get_back_and_main_menu_button()
        )
        await state.set_state(SearchInstallmentPlanState.number)
        return

    await message.answer(
        text="Начался поиск по номеру договора"
    )
    await base_show_installment_detail(
        number,
        message
    )


async def get_my_installment_plans(
        message: Message
):
    """Получение моих рассрочек"""
    user = await get_user(tg_user=message.from_user)

    phone_number = user.phone_number
    animation_stick = await message.answer_animation(
        animation="CAACAgEAAxkBAAIBo2ak68a67VdA58WBsOkyMYHPO0z0AALFAgACR4AZRNOTsbushnsaNQQ"
    )
    await asyncio.sleep(1.5)

    excel_data = get_excel_data()

    searched_data = find_rows_by_phone_number_for_me(
        phone_number=phone_number,
        rows_list=excel_data
    )

    if len(searched_data) == 0:
        await message.answer(
            text=f'По вашему номеру “{phone_number}” рассрочек не найдена, если вы считаете, что это ошибка, то сообщите об этом администратору - @{owner_admin}',
            reply_markup=await get_user_menu(user)
        )
        await animation_stick.delete()

        return

    await message.answer(
        text="Ваши рассрочки. Выберете ту, которая вас интересует:",
        reply_markup=generate_product_list_buttons(searched_data)
    )
    await animation_stick.delete()

async def add_excel_file_command(message: Message, state: FSMContext):
    """Отправка Excel файла"""
    await message.answer(
        text="Выберите файл (.xlsx):",
        reply_markup=await get_main_menu()
    )
    await state.set_state(ExcelFileState.file)

async def get_excel_file_command(message: Message, state: FSMContext):
    """Обработка полученного Excel файла"""
    global path
    user = await get_user(message.from_user)
    if message.text == ButtonText.back_button_text:
        await message.answer(
            text="Вы вернулись в главное меню",
            reply_markup=await get_user_menu(user)
        )
        await state.get_data()
        return
    try:
        excel_file = message.document.file_name

        if not excel_file.endswith('.xlsx'):
            raise ValueError("Выберите файл с форматом .xlsx")

        await message.answer(
            text=f'Началсь проверка и загрузка таблицы "{excel_file}"'
        )

        file_id = message.document.file_id
        file_info = await message.bot.get_file(file_id)

        path = 'documents/'
        downloaded_file = await message.bot.download_file(file_info.file_path)
        logging.info("Getting file")
        async with aiofiles.open(path + 'test.xlsx', 'wb') as file:
            await file.write(downloaded_file.read())

        excel_data = read_excel(f'{path}/test.xlsx')
        excel_data_list = excel_data.to_dict(orient='records')
        datas = excel_data_list.pop(0)

        if set(KEYS_FOR_GENERATE_MESSAGE).issubset(set(datas.keys())):
            [
                os.remove(
                    f'{path}/{file_name}'
                )
                for file_name in os.listdir(path)
                if 'file' in file_name
            ]

            downloaded_file = await message.bot.download_file(file_info.file_path)

            async with aiofiles.open(file_info.file_path, 'wb') as file:
                await file.write(downloaded_file.read())

            await message.answer(
                text="Данные обновились",
                reply_markup=await get_user_menu(user)
            )

            await state.clear()
            return

        else:
            await message.answer(
                text="Неверные столбцы в таблице\nПопробуйте отправить другой файл"
            )
            await state.get_data()

    except AttributeError as error:
        await message.answer(
            text=f"Проверьте корректность файла",
        )
        await state.set_state(ExcelFileState.file)
        return

    except ValueError as error:
        await message.answer(
            text="".join(error.args),
        )
        await state.set_state(ExcelFileState.file)
        return
    finally:
        os.remove(f'{path}/test.xlsx')
        logging.info("Remove test.xlsx")