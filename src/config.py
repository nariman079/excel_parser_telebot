import asyncio
import sys
from os import getenv
from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.data.sqlalchemy_ext import MappingBase

load_dotenv()

ACCESS_FOR_DATA_UPDATE = [
    'Alex_rumin', 'RonniKray', 'nariman079i'
]
KEYS_FOR_GENERATE_MESSAGE = [
    '№',
    'ФИО',
    'Номер телефона',
    'Товар',
    'Дата оф',
    'Общая Стоимость ',
    'Аванс',
    'М',
    'Опл. сумма',
    'факт остаток',
    'Проссрочка'
]

WORDS_FOR_REPLACE = [
    ('№:', 'Номер договора:'),
    ('ФИО:', 'ФИО:'),
    ('Номер телефона:', 'Номер телефона:'),
    ('Товар:', 'Товар:'),
    ('Дата оф:', 'Дата оформления:'),
    ('Общая Стоимость :', 'Стоимость товара в рассрочку:'),
    ('Аванс:', 'Аванс:'),
    ('М:', 'Срок рассрочки:'),
    ('Опл. сумма:', 'Оплаченная сумма по договору:'),
    ('факт остаток:', 'Фактический остаток:'),
    ('nan', "Информация отсутствует"),
    ('Проссрочка:', 'Сумма на просрочке:')
]

DEADLINE_TITLE = 'М'
PRODUCT_ROW_TITLE = 'Товар'
TIME_ROW_TITLE = "Дата оф"
NUMBER_ROW_TITLE = '№'

SITE_URL = 'https://ansar05.ru/'
WHATSAPP_URL = 'https://wa.me/message/SJ3CGLTME3CDP1'



current_directory: Path = Path.cwd()

if sys.platform == "win32":  # pragma: no cover
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


PRODUCTION_MODE: bool = getenv("PRODUCTION_MODE", "0") == "1"

if PRODUCTION_MODE:
    print(PRODUCTION_MODE)
    DB_URL = getenv("DB_LINK", None)
else:
    DB_URL = "postgresql+asyncpg://test:test@localhost:5431/test"
    print(DB_URL)
print(DB_URL)
# print(DB_URL, PRODUCTION_MODE)
convention = {
    "ix": "ix_%(column_0_label)s",  # noqa: WPS323
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # noqa: WPS323
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # noqa: WPS323
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # noqa: WPS323
    "pk": "pk_%(table_name)s",  # noqa: WPS323
}

engine = create_async_engine(
    DB_URL,
    pool_recycle=280,  # noqa: WPS432
    echo=not PRODUCTION_MODE,
)
db_meta = MetaData(naming_convention=convention)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase, MappingBase):
    __tablename__: str
    __abstract__: bool

    metadata = db_meta

