import os
from functools import wraps, partial
from pprint import pprint
from typing import Any

from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.config import KEYS_FOR_GENERATE_MESSAGE, WORDS_FOR_REPLACE, \
    ACCESS_FOR_DATA_UPDATE, SITE_URL, WHATSAPP_URL
from src.buttons import get_search_buttons, ButtonText, generate_product_list_buttons, generate_additional_button, \
    generate_url_button, get_full_menu_markup, get_control_buttons
from src.services.exel_services import get_excel_data, find_rows_by_phone_number, find_row_by_number
from src.utils import generate_message, replace_message
from src.buttons import get_organization_menu_markup


def is_numbers(phone: str) -> bool:
    """Проверка номера телефона"""
    return phone.isdigit()


def check_start(func):
    @wraps(func)
    def wrapper(self, message: Message = None, *args, **kwargs) -> Any:
        attrs = [self, ]
        print(func.__name__)

        if message:
            pprint(message)

            match message.text:
                case '/start':
                    self.bot.send_message(
                        chat_id=message.chat.id,
                        text="Вы отменили действие",
                        reply_markup=get_full_menu_markup(message.chat.username)
                    )
                    return
                case 'Главное меню':
                    self.bot.send_message(
                        chat_id=message.chat.id,
                        text="Вы вернулись в главное меню",
                        reply_markup=get_full_menu_markup(message.chat.username)
                    )
                    return
            attrs.append(message)
            return func(*attrs, *args, **kwargs)
        else:
            return func(*attrs, *args, **kwargs)

    return wrapper


class DecorateMethodsMeta(type):
    def __new__(cls, name, bases, dct):
        for attr, value in dct.items():
            if callable(value) and not attr.startswith("__"):
                if attr not in ['execute']:
                    dct[attr] = check_start(value)
        return super().__new__(cls, name, bases, dct)


class ShowInstallmentDetail(
    metaclass=DecorateMethodsMeta
):
    """
    Детальная информация о рассрочке клиента

    Поиск осуществляется по номеру договора
    """

    def __init__(
            self,
            bot: TeleBot,
            message: Message,
            product_number: int

    ):
        self.product_data = None
        self.telegram_id = message.chat.id
        self.bot = bot
        self.product_number = product_number
        self.message = message

    def __get_product(self) -> None:
        excel_data = get_excel_data()

        """Получение строки из таблицы"""
        self.product_data = find_row_by_number(
            self.product_number,
            excel_data
        )

    def __generate_and_send_message(self) -> None:
        """Генерация текста и отправка сообщения"""

        generated_message = generate_message(
            message_data=self.product_data,
            keys_for_generate=KEYS_FOR_GENERATE_MESSAGE
        )
        replaced_message = replace_message(
            message_text=generated_message,
            replaced_values=WORDS_FOR_REPLACE
        )

        self.bot.send_message(
            chat_id=self.telegram_id,
            text=replaced_message,
            reply_markup=get_full_menu_markup(self.message.chat.username)
        )

    def execute(self) -> None:
        """Выполнение команд"""

        self.__get_product()
        if not self.product_data:
            self.bot.send_message(
                chat_id=self.message.chat.id,
                text="Такого договора не найдено",
                reply_markup=get_full_menu_markup(self.message.chat.username)
            )
            return None
        self.__generate_and_send_message()
        return None


class GetInstallmentPlanData(
    metaclass=DecorateMethodsMeta
):
    def __init__(
            self,
            bot: TeleBot,
            message: Message

    ):
        self.telegram_id = message.chat.id
        self.bot = bot
        self.message = message
        self._start(message)

    def _start(self, message: Message, **kwargs):
        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Выберите способ поиска:",
            reply_markup=get_search_buttons()
        )
        self.bot.register_next_step_handler(
            message, self._get_search_method
        )

    def _get_search_method(self, message: Message, **kwargs) -> None:
        if message.text == ButtonText.back_button_text:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Вы вернулись на главное меню",
                reply_markup=get_full_menu_markup(self.message.chat.username)
            )
            return
        match message.text:
            case ButtonText.search_by_phone_number_button_text:
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="Отлично!\nВведите номер телефона:"
                )
                self.bot.register_next_step_handler(
                    message, self._search_by_phone_number
                )
            case ButtonText.search_by_number_button_text:
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="Отлично!\nВведите номер договора:"
                )
                self.bot.register_next_step_handler(
                    message, self._search_by_number
                )
            case _:
                self.bot.send_message(
                    chat_id=message.chat.id,
                    text="Выберите правильный способ поиска",
                    reply_markup=get_search_buttons()
                )
                self.bot.register_next_step_handler(
                    message, self._get_search_method
                )

    def _search_by_number(self, message: Message):
        """
        Поиск по номеру договора
        """
        if message.text == ButtonText.back_button_text:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Выберите способ поиска:",
                reply_markup=get_search_buttons()
            )
            self.bot.register_next_step_handler(
                message, self._get_search_method
            )
            return
        number = message.text
        if not is_numbers(number):
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Введите правильный номер договора"

            )
            self.bot.register_next_step_handler(
                message, self._search_by_number
            )
            return

        self.bot.send_message(
            chat_id=message.chat.id,
            text="Начался поиск по номеру договора"
        )

        ShowInstallmentDetail(
            bot=self.bot,
            message=message,
            product_number=int(number)
        ).execute()

    def _search_by_phone_number(self, message: Message):
        """
        Поиск по номеру телефона
        """
        if message.text == ButtonText.back_button_text:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Выберите способ поиска:",
                reply_markup=get_search_buttons()
            )
            self.bot.register_next_step_handler(
                message, self._get_search_method
            )
            return

        phone_number = message.text
        if not is_numbers(phone_number):
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Введите правильный номер телефона"
            )

            self.bot.register_next_step_handler(
                message, self._search_by_phone_number
            )
            return

        self.bot.send_message(
            chat_id=message.chat.id,
            text="Поиск по номеру телефона",
            reply_markup=ReplyKeyboardMarkup()
        )
        excel_data = get_excel_data()

        searched_data = find_rows_by_phone_number(
            phone_number=phone_number,
            rows_list=excel_data
        )
        if len(searched_data) == 0:
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Такого номера телефона в договорах не найдено",
                reply_markup=get_full_menu_markup(self.message.chat.username)
            )
            return

        self.bot.send_message(
            chat_id=message.chat.id,
            text="Ваши расскрочки:",
            reply_markup=generate_product_list_buttons(searched_data)
        )

        self.bot.send_message(
            chat_id=message.chat.id,
            text="Выберите чтобы посмотреть детальную информацию",
            reply_markup=get_full_menu_markup(self.message.chat.username)
        )


class AddExcelFile(
    metaclass=DecorateMethodsMeta
):
    """
    Добавленние новой информации о договорах
    """

    def __init__(
            self,
            bot: TeleBot,
            message: Message

    ):
        self.telegram_id = message.chat.id
        self.bot = bot
        self._start(message)

    def _start(self, message: Message) -> None:
        back_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        back_markup.row(*get_control_buttons())

        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Выберите файл (.xlsx):",
            reply_markup=back_markup
        )
        self.bot.register_next_step_handler(
            message, self._get_and_check_file
        )

    def _get_and_check_file(self, message: Message) -> None:
        if message.text == ButtonText.back_button_text:
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Вы вернулись в главное меню",
                reply_markup=get_full_menu_markup(message.chat.username)
            )
            return
        try:
            excel_file = message.document.file_name

            if not excel_file.endswith('.xlsx'):
                raise ValueError("Выберите файл с форматом .xlsx")

            self.bot.send_message(
                chat_id=self.telegram_id,
                text=f'Началсь загрузка таблицы "{excel_file}"'
            )

            file_id = message.document.file_id
            file_info = self.bot.get_file(file_id)

            path = 'documents/'

            [os.remove(f'{path}/{file_name}') for file_name in os.listdir(path)]

            downloaded_file = self.bot.download_file(file_info.file_path)

            with open(file_info.file_path, 'wb') as file:
                file.write(downloaded_file)

            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Данные обновились"
            )
        except AttributeError:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Проверьте правильность файла",
            )
            self.bot.register_next_step_handler(
                message, self._get_and_check_file
            )
            return
        except ValueError as error:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="".join(error.args),
            )
            self.bot.register_next_step_handler(
                message, self._get_and_check_file
            )
            return


class SendApplication:
    """ Событие для кнопки "Отправить заявку" """

    def __init__(
            self,
            bot: TeleBot,
            message: Message
    ):
        self.telegram_id = message.chat.id
        self.bot = bot
        self.message = message
        self.__start()

    def __start(self):
        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Нажмите чтобы перейти по ссылке:",
            reply_markup=generate_url_button(
                text="ansar05.ru",
                url=SITE_URL
            )
        )
        self.bot.send_message(
            chat_id=self.telegram_id,
            text="**************",
            reply_markup=get_full_menu_markup(self.message.chat.username)
        )


class MakePayment:
    """ Событие для кнопки "Совержить оплату" """

    def __init__(
            self,
            bot: TeleBot,
            message: Message
    ):
        self.telegram_id = message.chat.id
        self.bot = bot
        self.message = message
        self.__start()

    def __start(self):
        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Нажмите чтобы перейти по ссылке:",
            reply_markup=generate_url_button(
                text="Whatsapp",
                url=WHATSAPP_URL
            )
        )
        menu_markup = get_organization_menu_markup()

        if self.message.chat.username in ACCESS_FOR_DATA_UPDATE:
            menu_markup.add(generate_additional_button())

        self.bot.send_message(
            chat_id=self.telegram_id,
            text="**************",
            reply_markup=menu_markup
        )
