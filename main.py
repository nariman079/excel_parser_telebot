import os.path

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from src.buttons import ButtonText, get_organization_menu_markup, generate_additional_button, get_full_menu_markup, \
    back_markup
from src.config import ACCESS_FOR_DATA_UPDATE
from src.services.base_services import GetInstallmentPlanData, ShowInstallmentDetail, AddExcelFile, SendApplication, \
    MakePayment
from dotenv import load_dotenv

load_dotenv()


bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start_message(message: Message):
    menu_markup = get_organization_menu_markup()
    if message.from_user.username in ACCESS_FOR_DATA_UPDATE:
        menu_markup.add(generate_additional_button())
    bot.send_message(chat_id=message.chat.id,
                     text="Добро пожаловать",
                     reply_markup=menu_markup)


@bot.message_handler(content_types=['text'])
def button_text_handler(message: Message):
    match message.text:
        case ButtonText.send_application_button_text:
            SendApplication(
                bot=bot,
                message=message
            )
        case ButtonText.make_payment_button_text:
            MakePayment(
                bot=bot,
                message=message
            )
        case ButtonText.get_installment_plan_data_button_text:
            GetInstallmentPlanData(bot=bot, message=message)._start(message)
        case ButtonText.add_excel_file:
            if message.from_user.username in ACCESS_FOR_DATA_UPDATE:
                AddExcelFile(
                    bot=bot,
                    message=message
                )
        case ButtonText.main_menu_button_text:
            bot.send_message(
                chat_id=message.chat.id,
                text="Вы вернулись на главную",
                reply_markup=get_full_menu_markup(message.chat.username)
            )
        case ButtonText.search_by_number_button_text:
            bot.send_message(
                chat_id=message.chat.id,
                text="Отлично!\nВведите номер договора:",
                reply_markup=back_markup
            )
            bot.register_next_step_handler(
                message, GetInstallmentPlanData(bot=bot, message=message)._search_by_number
            )
        case ButtonText.search_by_phone_number_button_text:
            bot.send_message(
                chat_id=message.chat.id,
                text="Отлично!\nВведите номер телефона:",
                reply_markup=back_markup
            )
            bot.register_next_step_handler(
                message, GetInstallmentPlanData(bot=bot, message=message)._search_by_phone_number
            )
        case _:
            pass


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    data = call.data
    if 'product' in data:
        ShowInstallmentDetail(
            bot=bot,
            message=call.message,
            product_number=int(data.replace('product_', ''))
        ).execute()


if __name__ == '__main__':
    if os.path.isdir('documents/'):
        pass
    else:
        os.mkdir('documents/')
    bot.infinity_polling()
