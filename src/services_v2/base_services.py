import asyncio
import os

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from pandas import read_excel
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.buttons_v2 import get_back_markup, ButtonText, get_full_menu_markup, generate_url_button, get_search_buttons, \
    generate_product_list_buttons, get_confirm_buttons, get_access_phone_number_buttons
from src.config import KEYS_FOR_GENERATE_MESSAGE, WHATSAPP_URL, SITE_URL, WORDS_FOR_REPLACE
from src.services.exel_services import get_excel_data, find_rows_by_phone_number, find_row_by_number
from src.state_groups import ExcelFileState, SearchInstallmentPlanState, CreateAdminUserState, GetContactUser
from src.utils import replace_message, generate_message
from src.data.models import User
from src.data.db_services import db_action, get_user, delete_admin, add_admin, create_user, create_or_update_v2


def is_numbers(phone: str) -> bool:
    """Проверка номера телефона"""
    return phone.isdigit()


@db_action
async def get_user(
        session: AsyncSession,
        **kwargs
) -> User:
    username: str = kwargs.get('username')
    users = await session.execute(
        select(
            User
        ).where(
            User.username == username
        )
    )
    return users.scalars().first()


@db_action
async def create_user(
        session: AsyncSession,
        **kwargs
) -> User:
    session.add(
        kwargs.get('user')
    )
    return kwargs.get('user')

@db_action
async def create_or_update(
        session: AsyncSession,
        **kwargs
) -> User:
    session.add(
        kwargs.get('user')
    )
    return kwargs.get('user')


@db_action
async def delete_objects(
        session: AsyncSession,
        **kwargs
) -> int:
    """
    Удаление списка объектов из БД
    """
    await session.execute(
        delete(User).where(
            User.username.in_(kwargs.get('username_list'))
        )
    )
    return len(kwargs.get('username_list'))


@db_action
async def update_user(
        session: AsyncSession,
        **kwargs
) -> str:
    d = await session.execute(
        update(
            User
        )
        .where(
            User.username == kwargs.get('username')
        ).values(
            is_admin=kwargs.get('is_admin')
        )
    )
    print(d.first().__dict__)
    return kwargs.get('username')


class AddExcelFile:
    """
    Добавленние новой информации о договорах
    """

    @staticmethod
    async def start(message: Message, state: FSMContext) -> None:
        await message.answer(
            text="Выберите файл (.xlsx):",
            reply_markup=ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(
                        text=ButtonText.main_menu_button_text
                    )
                ]
            ])
        )
        await state.set_state(ExcelFileState.file)

    @staticmethod
    async def get_and_check_file(message: Message, state: FSMContext) -> None:
        if message.text == ButtonText.back_button_text:
            await message.answer(
                text="Вы вернулись в главное меню",
                reply_markup=await get_full_menu_markup(message.chat.username)
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
                    reply_markup=await get_full_menu_markup(message.chat.username)
                )
                os.remove(f'{path}/test.xlsx')
                await state.clear()
                return

            else:
                await message.answer(
                    text="Неверные столбцы в таблице\nПопробуйте отравить другой файл"
                )
                await state.get_data()

        except AttributeError as error:
            await message.answer(
                text=f"Проверьте правильность файла",
            )
            await state.set_state(ExcelFileState.file)
            return
        except ValueError as error:
            await message.answer(
                text="".join(error.args),
            )
            await state.set_state(ExcelFileState.file)
            return


class SingleAction:
    """
    Одиночные события

    1 Отправить заявку
    2 Совершить оплату
    """

    @staticmethod
    async def make_payment(message: Message):
        await message.answer(
            text="Нажмите чтобы перейти по ссылке:",
            reply_markup=generate_url_button(
                text="Whatsapp",
                url=WHATSAPP_URL
            )
        )

    @staticmethod
    async def send_application(message: Message):
        await message.answer(
            text="Нажмите чтобы перейти по ссылке:",
            reply_markup=generate_url_button(
                text="ansar05.ru",
                url=SITE_URL
            )
        )


class ShowInstallmentDetail(
):
    """
    Детальная информация о рассрочке клиента

    Поиск осуществляется по номеру договора
    """

    def __init__(
            self,
            product_number: int,
            message: Message

    ):
        self.product_data = None
        self.message = message
        self.product_number = product_number

    async def _get_product(self) -> None:
        """Получение строки из таблицы"""

        excel_data = get_excel_data()

        self.product_data = find_row_by_number(
            self.product_number,
            excel_data
        )

    async def _generate_and_send_message(self) -> None:
        """Генерация текста и отправка сообщения"""

        generated_message = generate_message(
            message_data=self.product_data,
            keys_for_generate=KEYS_FOR_GENERATE_MESSAGE
        )
        replaced_message = replace_message(
            message_text=generated_message,
            replaced_values=WORDS_FOR_REPLACE
        )

        await self.message.answer(
            text=replaced_message,
            reply_markup=await get_full_menu_markup(self.message.chat.username)
        )

    async def execute(self) -> None:
        """Выполнение команд"""

        await self._get_product()
        if not self.product_data:
            await self.message.answer(
                text=f"Рассрочка с договором №{self.message.text} не найдена.",
                reply_markup=await get_full_menu_markup(self.message.chat.username)
            )
            return None
        await self._generate_and_send_message()
        return None


class GetInstallmentPlanData:

    @staticmethod
    async def start(message: Message, state: FSMContext):
        await message.answer(
            text="Выберите способ поиска:",
            reply_markup=get_search_buttons()
        )
        await state.set_state(SearchInstallmentPlanState.search_type)

    @staticmethod
    async def get_search_method(message: Message, state: FSMContext) -> None:
        if message.text == ButtonText.back_button_text:
            await message.answer(
                text="Вы вернулись на главное меню",
                reply_markup=await get_full_menu_markup(message.chat.username)
            )
            return
        match message.text:
            case ButtonText.search_by_phone_number_button_text:
                await message.answer(
                    text="Введите номер телефона:\nПример: 89280001288",
                    reply_markup=ReplyKeyboardMarkup(
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
                )
                await state.set_state(SearchInstallmentPlanState.phone_number)
            case ButtonText.search_by_number_button_text:
                await message.answer(
                    text="Введите номер договора:\nПример: 324",
                    reply_markup=ReplyKeyboardMarkup(
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
                )
                await state.set_state(SearchInstallmentPlanState.number)
            case _:
                await message.answer(
                    text="Выберите правильный способ поиска",
                    reply_markup=get_back_markup()
                )
                await state.set_state(SearchInstallmentPlanState.search_type)

    @staticmethod
    async def search_by_number(message: Message, state: FSMContext):
        """
        Поиск по номеру договора
        """
        try:
            if message.text == ButtonText.back_button_text:
                await message.answer(
                    text="Выберите способ поиска:",
                    reply_markup=get_search_buttons()
                )
                await state.set_state(SearchInstallmentPlanState.search_type)
                return
            number = message.text
            if not is_numbers(number):
                await message.answer(
                    text="Попробуйте еще раз!\nВведите правильный номер договора\nПример: 943",
                    reply_markup=get_back_markup()
                )
                await state.set_state(SearchInstallmentPlanState.number)
                return

        except Exception:
            await message.answer(
                text="Попробуйте еще раз!\nВведите правильный номер договора\nПример: 943",
                reply_markup=get_back_markup()
            )
            await state.set_state(SearchInstallmentPlanState.number)
            return

        await message.answer(
            text="Начался поиск по номеру договора"
        )

        await ShowInstallmentDetail(
            message=message,
            product_number=int(number)
        ).execute()

    @staticmethod
    async def search_by_phone_number(
            message: Message,
            state: FSMContext
    ) -> None:
        """
        Поиск по номеру телефона
        """
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
                    reply_markup=ReplyKeyboardMarkup(
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
                )
                await state.set_state(SearchInstallmentPlanState.phone_number)
                return

        except Exception as error:
            print(error.args)
            await message.answer(
                text="Попробуйте еще раз!\nВведите правильный номер телефона\nПример: 89280001288",
                reply_markup=ReplyKeyboardMarkup(
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
            )
            await state.set_state(SearchInstallmentPlanState.phone_number)

            return

        await message.answer(
            text="Поиск по номеру телефона",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[

                ]
            )
        )
        excel_data = get_excel_data()

        searched_data = find_rows_by_phone_number(
            phone_number=phone_number,
            rows_list=excel_data
        )
        if len(searched_data) == 0:
            await message.answer(
                text="Такого номера телефона в договорах не найдено",
                reply_markup=await get_full_menu_markup(message.chat.username)
            )
            return

        await message.answer(
            text="Найденные рассрочки",
            reply_markup=generate_product_list_buttons(searched_data)
        )

        await message.answer(
            text="Выберите чтобы посмотреть детальную информацию",
            reply_markup=await get_full_menu_markup(message.chat.username)
        )

        await state.clear()


class CreateAdminUser:
    @staticmethod
    async def start(message: Message, state: FSMContext) -> None:
        await message.answer(
            text="Введите username пользователя с @:",
            reply_markup=get_back_markup()
        )
        await state.set_state(CreateAdminUserState.username)

    @staticmethod
    async def get_username(message: Message, state: FSMContext) -> None:
        username = message.text

        if '@' in username:
            username = username[1:]

        user = await get_user(username=username)

        if not user:
            await create_user(
                user=User(
                    username=username
                )
            )
            await message.answer(
                text=f"Администратор {username} успешно создан ",
                reply_markup=await get_full_menu_markup(message.chat.username)
            )
            await state.clear()
            return
        elif user.is_admin:
            await message.answer(
                text="Такой администратор уже есть в Базе данных, хотите удалить его?",
                reply_markup=get_confirm_buttons(username)
            )
        else:
            await add_admin(username=username)
            await message.answer(
                text=f"Администратор {username} успешно создан ",
                reply_markup=await get_full_menu_markup(message.chat.username)
            )
        await state.clear()


class DeleteAdminUser:
    @staticmethod
    async def delete_admin(username: str, message: Message) -> None:
        await delete_admin(username=username)
        await message.answer(
            text=f"Администратор {username} удален из системы",
            reply_markup=await get_full_menu_markup(message.chat.username)
        )


class StartHandler:
    @staticmethod
    async def get_or_create_user(message: Message, state: FSMContext) -> None:
        tg_user = message.from_user
        db_user = await get_user(username=tg_user.username)
        if db_user:
            if db_user.phone_number and db_user.is_admin:
                await message.answer(
                    text="Добро пожаловать в <a href='https://ansar05.ru'>Ansar Finance</a> bot.\nВы являетесь администратором.",
                    reply_markup=await get_full_menu_markup(tg_user.username)
                )
                return
            elif db_user.phone_number and not db_user.is_admin:
                await message.answer(
                    text="Добро пожаловать в <a href='https://ansar05.ru'>Ansar Finance</a> bot.",
                    reply_markup=await get_full_menu_markup(tg_user.username)
                )
                return
            elif not db_user.phone_number and db_user.is_admin:
                await message.answer(
                    text="Разрешите доступ к номеру телефона для работы с ботом",
                    reply_markup=get_access_phone_number_buttons()
                )
                await state.set_state(GetContactUser.phone_number)
                return
            elif not db_user.phone_number and not db_user.is_admin:
                await message.answer(
                    text="Разрешите доступ к номеру телефона для работы с ботом",
                    reply_markup=get_access_phone_number_buttons()
                )
                await state.set_state(GetContactUser.phone_number)
            else:
                pass
        else:
            await message.answer(
                text="Разрешите доступ к номеру телефона для работы с ботом",
                reply_markup=get_access_phone_number_buttons()
            )
            await state.set_state(GetContactUser.phone_number)

    @staticmethod
    async def get_phone_number(message: Message, state: FSMContext):
        tg_user = message.from_user
        if message.contact:
            new_user = User(
                username=tg_user.username,
                telegram_id=str(tg_user.id),
                phone_number=message.contact.phone_number
            )
            await create_or_update_v2(
                username=tg_user.username,
                updated_data=new_user
            )
            await message.answer(
                text="Добро пожаловать в Ansar Finance Bot",
                reply_markup=await get_full_menu_markup(tg_user.username)
            )
        await state.clear()


async def search_my_installment_plan(
        message: Message,
) -> None:
    """
    Поиск по номеру телефона
    """
    user = await get_user(username=message.chat.username)

    print(user, 'dffffffffffffffffffffffffffffffffffffffffffffffffffff')
    phone_number = user.phone_number
    animation_stick = await message.answer_animation(
    animation="CAACAgEAAxkBAAIBo2ak68a67VdA58WBsOkyMYHPO0z0AALFAgACR4AZRNOTsbushnsaNQQ"
    )
    await asyncio.sleep(1.5)

    excel_data = get_excel_data()

    searched_data = find_rows_by_phone_number(
        phone_number=phone_number,
        rows_list=excel_data
    )

    if len(searched_data) == 0:
        await message.answer(
            text=f'По вашему номеру “{phone_number}” рассрочек не найдено',
            reply_markup=await get_full_menu_markup(message.chat.username)
        )
        await animation_stick.delete()

        return

    await message.answer(
        text="Ваши рассрочки. Выберете ту, которая вас интересует:",
        reply_markup=generate_product_list_buttons(searched_data)
    )
    await animation_stick.delete()

