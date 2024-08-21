from src.buttons.main_buttons import get_user_menu, get_start_text
from src.buttons.main_buttons import ButtonText
from src.data.models import User


async def generate_message_args(user: User) -> dict:
    """ Генерация аргументов для сообщения start """
    text = await get_start_text(user)
    reply_markup = await get_user_menu(user)

    return dict(
        text=text,
        reply_markup=reply_markup
    )


