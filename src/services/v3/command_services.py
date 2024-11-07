from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.util import await_only

from src.buttons.main_buttons import get_main_menu, get_user_menu, get_confirm_buttons, get_search_variant_buttons, \
    ButtonText, get_back_button, get_back_and_main_menu_button
from src.services.v3.base_services import generate_message_args, generate_single_action_message_args, \
    generate_installment_detail_message_args, generate_search_type_message_args
from src.services.v3.user_services import get_user, create_or_update_user, get_custom_user, get_admin_user, \
    generate_admin_user, create_admin_user, delete_admin_user
from src.services_v2.base_services import is_numbers
from src.state_groups import CreateAdminUserState, SearchInstallmentPlanState


async def base_show_installment_detail(
        product_number: str | int,
        message: Message,
) -> None:
    """"""
    user = await get_user(message.from_user)
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

    if '@' in username:
        username = username[1:]

    admin_user = await generate_admin_user(username)
    user = await get_admin_user(admin_user)

    if not user:
        await create_admin_user(username)
        await message.answer(
            text=f"Администратор {username} успешно создан ",
            reply_markup=await get_user_menu(my_user)
        )
    elif user and user.is_admin:
        await message.answer(
            text="Такой администратор уже есть в Базе данных, хотите удалить его?",
            reply_markup=await get_confirm_buttons(username)
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
    user = await get_user(message.from_user)
    await callback.message.delete()
    if deleted_admin:
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
    print(user)


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
    try:
        if message.text == ButtonText.back_button_text:
            await message.answer(
                text="Выберите способ поиска:",
                reply_markup=get_search_buttons()
            )
            await state.set_state(SearchInstallmentPlanState.search_type)
            return
        phone_number = message.text
        if not is_numbers(phone_number):
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
        if not is_numbers(number):
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
 