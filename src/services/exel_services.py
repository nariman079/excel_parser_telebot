import os

from pandas import read_excel


def get_first_obj(objects: list):
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


def find_row_by_number(
        id_: int,
        rows_list: list[dict]
) -> dict | None:
    """Поиск строки по ID в списке"""
    result_data = filter(
        lambda x: int(x['№']) == id_,
        rows_list
    )
    return get_first_obj(list(result_data))


def find_rows_by_phone_number(
        phone_number: str,
        rows_list: list[dict]
) -> list[dict] | None:
    """Поиск строки по ID в списке"""
    result_data = filter(
        lambda x: int(x['Номер телефона']) == int(phone_number),
        rows_list
    )
    return list(result_data)
