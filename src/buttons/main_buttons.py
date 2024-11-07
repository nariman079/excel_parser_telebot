from pickle import SETITEMS

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from src.data.models import User


class ButtonText:
    """Все строки и тексты бота"""
    welcome_for_admin_text = "Добро пожаловать в <a href='https://ansar05.ru'>Ansar Finance</a> bot.\nВы являетесь администратором."
    welcome_for_custom_user_text = "Добро пожаловать в <a href='https://ansar05.ru'>Ansar Finance</a> bot."
    send_application_button_text = "Отправить заявку"
    make_payment_button_text = 'Совершить оплату'
    get_installment_plan_data_button_text = 'Данные по рассрочке'

    search_by_number_button_text = "Поиск по № договора"
    search_by_phone_number_button_text = "Поиск по номеру телефона"

    add_excel_file = "Обновить excel"

    back_button_text = "Назад"
    main_menu_button_text = "Главное меню"

    add_admin_button_text = "Добавить админа"
    my_installment_plans = "Мои рассрочки"

    get_access_phone_number_text = "Разрешить доступ к номеру телефона"


async def get_admin_menu() -> ReplyKeyboardMarkup:
    """Получение меню для администратора"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=ButtonText.get_installment_plan_data_button_text
                ),
            ],
            [
                KeyboardButton(
                    text=ButtonText.make_payment_button_text
                ),
                KeyboardButton(
                    text=ButtonText.send_application_button_text
                )
            ],
            [
                KeyboardButton(
                    text=ButtonText.add_excel_file
                ),
                KeyboardButton(
                    text=ButtonText.add_admin_button_text
                )
            ]
        ]
    )


async def get_custom_user_menu() -> ReplyKeyboardMarkup:
    """Получение меню для обычного пользователя"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=ButtonText.my_installment_plans
                ),
            ],
            [
                KeyboardButton(
                    text=ButtonText.make_payment_button_text
                ),
                KeyboardButton(
                    text=ButtonText.send_application_button_text
                )
            ],
        ]
    )


async def get_search_variant_buttons() -> ReplyKeyboardMarkup:
    """Получение выпора поиска"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=ButtonText.search_by_number_button_text
                ),
            ],
            [
                KeyboardButton(
                    text=ButtonText.search_by_phone_number_button_text
                )
            ],
            [
                KeyboardButton(
                    text=ButtonText.main_menu_button_text
                )
            ]
        ]
    )

async def get_phone_number() -> ReplyKeyboardMarkup:
    """Получение номера телефона"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=ButtonText.get_access_phone_number_text,
                    request_contact=True,
                )
            ]
        ]
    )


async def get_main_menu() -> ReplyKeyboardMarkup:
    """Получение кнопки главное меню"""
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text=ButtonText.main_menu_button_text,
                )
            ]
        ]
    )


async def generate_user_menu(user: User | None) -> ReplyKeyboardMarkup:
    """Проверка и генерация меню для пользователя"""
    if not user:
        return await get_phone_number()
    elif user.is_admin and not user.phone_number:
        return await get_phone_number()
    elif user.is_admin and user.phone_number:
        return await get_admin_menu()
    elif not user.is_admin and user.phone_number:
        return await get_custom_user_menu()
    elif not user.is_admin and not user.phone_number:
        return await get_phone_number()


async def generate_inline_button(
        text: str,
        url: str
) -> InlineKeyboardMarkup:
    """Герерация текстовой кнопки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    url=url
                )
            ]
        ]
    )


async def generate_start_text(user: User | None) -> str:
    """Проверка и генерация меню для пользователя"""
    if not user:
        return ButtonText.get_access_phone_number_text
    elif user.is_admin and not user.phone_number:
        return ButtonText.get_access_phone_number_text
    elif user.is_admin and user.phone_number:
        return ButtonText.welcome_for_admin_text
    elif not user.is_admin and user.phone_number:
        return ButtonText.welcome_for_custom_user_text
    elif not user.is_admin and not user.phone_number:
        return ButtonText.get_access_phone_number_text
    else:
        return ButtonText.get_access_phone_number_text


async def get_confirm_buttons(username: str) -> InlineKeyboardMarkup:
    """Кнопки для подтверждения удаления админа"""
    confirm_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=f"delete-{username}"
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data="cancelled"
                )
            ]
        ]
    )
    return confirm_buttons

async def get_back_and_main_menu_button():
    return ReplyKeyboardMarkup(
                        resize_keyboard=True,
                        keyboard=[
                            [
                                KeyboardButton(
                                    text=ButtonText.back_button_text
                                ),
                                KeyboardButton(
                                    text=ButtonText.main_menu_button_text
                                )
                            ]
                        ]
                )


async def get_back_button():
    return ReplyKeyboardMarkup(
                        resize_keyboard=True,
                        keyboard=[
                            [
                                KeyboardButton(
                                    text=ButtonText.back_button_text
                                )
                            ]
                        ]
                )


async def get_user_menu(user: User) -> ReplyKeyboardMarkup:
    """Получение меню пользователя"""
    return await generate_user_menu(user)


async def get_start_text(user: User) -> str:
    """Получение сообщения при старте"""
    return await generate_start_text(user)

