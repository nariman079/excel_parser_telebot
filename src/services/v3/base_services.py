from src.buttons.main_buttons import get_user_menu, get_start_text, generate_inline_button, \
    get_back_and_main_menu_button
from src.buttons.message_buttons import generate_message, replace_message
from src.config import KEYS_FOR_GENERATE_MESSAGE, WORDS_FOR_REPLACE
from src.data.models import User
from src.services.exel_services import find_row_by_number, get_excel_data


async def generate_message_args(user: User) -> dict:
    """Генерация именованных аргументов для сообщения start"""
    text = await get_start_text(user)
    reply_markup = await get_user_menu(user)

    return dict(
        text=text,
        reply_markup=reply_markup
    )


async def generate_single_action_message_args(
        text: str,
        inline_url: str,
        inline_text: str
) -> dict:
    """Генерация именованных аргументов одиночных сообщений"""
    reply_markup = await generate_inline_button(
        url=inline_url,
        text=inline_text
    )
    return dict(
        text=text,
        reply_markup=reply_markup
    )


async def generate_installment_detail_message_args(
        product_number: str | int,
        user: User
) -> dict:
    """
    Генерация именованных аргументов
    для детальной информации договора
    """
    excel_data = get_excel_data()
    product_data = find_row_by_number(
        product_number,
        excel_data
    )
    if not product_data:
        return dict(
            text=f"Рассрочка с договором №{product_number} не найдена.",
            reply_markup=await get_user_menu(user)
        )

    generated_message = await generate_message(
        product_data,
        KEYS_FOR_GENERATE_MESSAGE
    )
    replaced_message = await replace_message(
        generated_message,
        WORDS_FOR_REPLACE
    )
    return dict(
        text=replaced_message,
        reply_markup=await get_user_menu(user)
    )

async def generate_installment_detail_message_args(
        product_number: str | int,
        user: User
) -> dict:
    """
    Генерация именованных аргументов
    для детальной информации договора
    """
    excel_data = get_excel_data()
    product_data = find_row_by_number(
        product_number,
        excel_data
    )
    if not product_data:
        return dict(
            text=f"Рассрочка с договором №{product_number} не найдена.",
            reply_markup=await get_user_menu(user)
        )

    generated_message = await generate_message(
        product_data,
        KEYS_FOR_GENERATE_MESSAGE
    )
    replaced_message = await replace_message(
        generated_message,
        WORDS_FOR_REPLACE
    )
    return dict(
        text=replaced_message,
        reply_markup=await get_user_menu(user)
    )


async def generate_search_type_message_args(
        text: str
):

    return dict(
        text=text,
        reply_markup=await get_back_and_main_menu_button()
    )

