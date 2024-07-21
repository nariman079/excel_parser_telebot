from enum import StrEnum

from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from src.config import PRODUCT_ROW_TITLE, NUMBER_ROW_TITLE, ACCESS_FOR_DATA_UPDATE


class ButtonText(StrEnum):
    send_application_button_text = "Отправить заявку"
    make_payment_button_text = 'Совершить оплату'
    get_installment_plan_data_button_text = 'Данные по рассрочке'

    search_by_number_button_text = "Поиск по № договора"
    search_by_phone_number_button_text = "Поиск по номеру телефона"

    add_excel_file = "Добавить excel файл"

    back_button_text = "Назад"
    main_menu_button_text = "Главное меню"

def get_control_buttons() -> tuple:
    back_button = KeyboardButton(
        ButtonText.back_button_text
    )
    main_menu_button = KeyboardButton(
        ButtonText.main_menu_button_text
    )
    
    return back_button, main_menu_button
    
def get_organization_menu_markup() -> ReplyKeyboardMarkup:
    """
    Генерация кнопок для меню

    Кнопка "Отправить заявку"
    Кнопка "Совершить оплату"
    Кнопка "Данные по рассрочке"
    """

    organization_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)

    send_application_button = KeyboardButton(
        ButtonText.send_application_button_text
    )
    make_payment_button = KeyboardButton(
        ButtonText.make_payment_button_text
    )
    get_installment_plan_data_button = KeyboardButton(
        ButtonText.get_installment_plan_data_button_text
    )

    organization_menu_markup.add(get_installment_plan_data_button)
    organization_menu_markup.row(make_payment_button, send_application_button)

    return organization_menu_markup


def generate_additional_button() -> KeyboardButton:
    """Геренация дополнительной кнопки для добавления excel файла"""
    result_button = KeyboardButton(
        text=ButtonText.add_excel_file
    )
    return result_button


def generate_url_button(
        text: str,
        url: str,
) -> InlineKeyboardMarkup:
    """Генерация кнопок для переадресации"""

    url_button = InlineKeyboardMarkup()
    url_button.add(
        InlineKeyboardButton(
            text=text,
            url=url
        )
    )
    return url_button


def get_search_buttons() -> ReplyKeyboardMarkup:
    """
    Генерация кнопок для поиска

    По номеру договора
    По номеру телефона
    """
    search_markup = ReplyKeyboardMarkup(resize_keyboard=True)

    search_by_number_button = KeyboardButton(
        ButtonText.search_by_number_button_text
    )
    search_by_phone_number_button = KeyboardButton(
        ButtonText.search_by_phone_number_button_text
    )
    
    search_markup.add(search_by_number_button)
    search_markup.add(search_by_phone_number_button)
    search_markup.row(*get_control_buttons())

    return search_markup


def generate_product_list_buttons(installment_rows: list[dict]) -> InlineKeyboardMarkup:
    """Генерация списка товаров в виде InlineKeyboardButton"""

    product_inline_markup = InlineKeyboardMarkup()

    [
        product_inline_markup.add(InlineKeyboardButton(
            text=row[PRODUCT_ROW_TITLE],
            callback_data=f"product_{int(row[NUMBER_ROW_TITLE])}"
        ))
        for row in installment_rows
    ]
    return product_inline_markup


def get_full_menu_markup(username: str) -> ReplyKeyboardMarkup:
    menu_markup = get_organization_menu_markup()

    if username in ACCESS_FOR_DATA_UPDATE:
        menu_markup.add(generate_additional_button())

    return menu_markup


back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
back_markup.row(*get_control_buttons())
