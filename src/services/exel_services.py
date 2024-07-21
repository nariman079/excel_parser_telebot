import os

from pandas import read_excel, notnull


def get_first_obj(objects: list):
    """Получение первого объекта со списка"""
    if len(objects) == 0:
        return None
    return objects[0]


def get_excel_data(

) -> list[dict] | None:
    """ Получение и преобразование файла """
    path = 'documents/'
    file_in_dir = os.listdir(path)[0]
    excel_data = read_excel(f'{path}/{file_in_dir}')
    excel_data_list = excel_data.to_dict(orient='records')
    excel_data_list.pop(-1)
    return excel_data_list


def num_filter(num: int, row_str: int):
    try:
        return int(row_str) == int(num)
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
