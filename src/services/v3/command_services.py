from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.buttons.main_buttons import get_main_menu, get_user_menu, get_confirm_buttons
from src.data.db_services import delete_admin
from src.services.v3.base_services import generate_message_args
from src.services.v3.user_services import get_user, create_or_update_user, get_custom_user, get_admin_user, \
    generate_admin_user, create_admin_user, delete_admin_user
from src.state_groups import CreateAdminUserState


async def start_handler(message: Message) -> None:
    """Обработчик команды /start"""
    tg_user = message.from_user
    db_user = await get_user(tg_user)
    message_args = await generate_message_args(db_user)

    await message.answer(
        **message_args
    )


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
            text="Произошла ошибка попробуйте чуть позже",
            reply_markup=await get_user_menu(user)
        )
