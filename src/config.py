import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')


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
