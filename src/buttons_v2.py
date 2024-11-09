from enum import StrEnum

from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup)

from src.config import PRODUCT_ROW_TITLE, NUMBER_ROW_TITLE
from src.data.models import User


class ButtonText(StrEnum):
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


def get_organization_menu_markup() -> ReplyKeyboardMarkup:
    """
    Генерация кнопок для меню

    Кнопка "Отправить заявку"
    Кнопка "Совершить оплату"
    Кнопка "Данные по рассрочке"
    """
    send_application_button = KeyboardButton(
        text=ButtonText.send_application_button_text
    )
    make_payment_button = KeyboardButton(
        text=ButtonText.make_payment_button_text
    )

    organization_menu_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                make_payment_button, send_application_button
            ]
        ]
    )
    return organization_menu_markup


def generate_additional_button() -> list[KeyboardButton]:
    """Геренация дополнительной кнопки для добавления excel файла"""
    get_installment_plan_data_button = KeyboardButton(
        text=ButtonText.get_installment_plan_data_button_text
    )
    result_button = [KeyboardButton(
        text=ButtonText.add_excel_file
    ), KeyboardButton(
        text=ButtonText.add_admin_button_text
    ), get_installment_plan_data_button]

    return result_button


def generate_url_button(
        text: str,
        url: str,
) -> InlineKeyboardMarkup:
    """Генерация кнопок для переадресации"""

    url_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    url=url

                )
            ]
        ]
    )
    return url_button


def generate_product_list_buttons(installment_rows: list[dict]) -> InlineKeyboardMarkup:
    """Генерация списка товаров в виде InlineKeyboardButton"""

    product_inline_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=str(row[PRODUCT_ROW_TITLE]),
                callback_data=f"product_{row[NUMBER_ROW_TITLE]}"
            )] for row in installment_rows
        ]
    )
    return product_inline_markup


async def get_full_menu_markup(username: str) -> ReplyKeyboardMarkup:
    menu_markup = get_organization_menu_markup()

    user = await User.find_first_by_kwargs(username=username)

    if user and user.is_admin:
        admin_buttons = generate_additional_button()
        menu_markup.keyboard.append([admin_buttons[0], admin_buttons[1]])
        menu_markup.keyboard.insert(0, [admin_buttons[-1]])
    else:
        menu_markup.keyboard.insert(0,
                                    [
                                        KeyboardButton(
                                            text=ButtonText.my_installment_plans
                                        )
                                    ]
                                    )
    return menu_markup


def get_back_markup() -> ReplyKeyboardMarkup:
    back_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=ButtonText.main_menu_button_text)
            ]
        ]
    )
    return back_markup


def get_search_buttons() -> ReplyKeyboardMarkup:
    """
    Генерация кнопок для поиска

    По номеру договора
    По номеру телефона
    """

    search_markup = ReplyKeyboardMarkup(
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
    return search_markup


def get_confirm_buttons(username: str) -> InlineKeyboardMarkup:
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


def get_access_phone_number_buttons() -> ReplyKeyboardMarkup:
    access_phone_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(
                    text="Разрешить доступ к номеру телефона",
                    request_contact=True,
                ),
            ]
        ]
    )
    return access_phone_markup
