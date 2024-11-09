import os
import re

from pandas import read_excel
from sqlalchemy.util import await_only


def get_first_obj(objects: list):
    """Получение первого объекта со списка"""
    if len(objects) == 0:
        return None
    return objects[0]


def get_excel_data() -> list[dict] | None:
    """ Получение и преобразование файла """
    path = 'documents/'
    file_in_dir = os.listdir(path)[0]
    excel_data = read_excel(f'{path}/{file_in_dir}')
    excel_data_list = excel_data.to_dict(orient='records')
    excel_data_list.pop(-1)
    return excel_data_list


def cln_phone(phone_number):
    # Регулярное выражение для поиска префиксов +7 или 8 в начале строки
    regex = r'^\+7|^8|^7'
    # Замена найденного префикса на пустую строку
    cleaned_phone_number = re.sub(regex, '', phone_number)
    return cleaned_phone_number


def num_filter(num: int, row_str: int):
    try:
        return cln_phone(str(num)) == cln_phone(str(row_str))
    except Exception as error:
        print(error.args)
        return False


def find_row_by_number(
        id_: int,
        rows_list: list[dict]
) -> dict | None:
    """Поиск строки по ID в списке"""
    result_data = filter(
        lambda x: num_filter(id_, x['№']),
        rows_list
    )
    return get_first_obj(list(result_data))


def find_rows_by_phone_number(
        phone_number: str,
        rows_list: list[dict]
) -> list[dict] | None:
    """Поиск строки по ID в списке"""

    result_data = filter(
        lambda x: num_filter(phone_number, x['Номер телефона']),
        rows_list
    )
    return list(result_data)


def find_rows_by_phone_number_for_me(
        phone_number: str,
        rows_list: list[dict]
) -> list[dict] | None:
    """Поиск строки по ID в списке"""

    result_data = filter(
        lambda x: num_filter(phone_number, x['Номер телефона']),
        rows_list
    )
    return list(result_data)



async def find_row(
        id_: int | str,
        field_name: str,
        rows_list: list[dict]
) -> dict | None:
    """Поиск строки по полю и ID или Номеру телефона"""
    result_data = filter(
        lambda x: num_filter(id_, x[field_name]),
        rows_list
    )
    return get_first_obj(list(result_data))


async def find_row_number(
        id_: int,
        row_list: list[dict]
) -> dict | None:
    """Поиск строки по ID"""
    return await find_row(
        id_,
        '№',
        row_list
    )


async def find_row_phone_number(
        phone_number: int,
        row_list: list[dict]
) -> dict | None:
    """Поиск строки по номеру телефона"""
    return await find_row(
        phone_number,
        'Номер телефона',
        row_list
    )