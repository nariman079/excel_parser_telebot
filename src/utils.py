import datetime

from src.config import DEADLINE_TITLE, TIME_ROW_TITLE


def get_month_label(number):
    if number % 10 == 1 and number % 100 != 11:
        return f"{number} месяц"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return f"{number} месяца"
    else:
        return f"{number} месяцев"


def replace_message(
        message_text: str,
        replaced_values: list[tuple]
) -> str:
    """ Изменение отображения ключей в сооющении """
    result_message = message_text
    for i in replaced_values:
        result_message = result_message.replace(*i)

    return result_message


def generate_message(
        message_data: dict,
        keys_for_generate: list[str]
):
    """ Генерация сообщения для отправки в телеграм """
    result_message = ""

    for key, value in message_data.items():

        if key in keys_for_generate:
            if key == DEADLINE_TITLE:
                value = get_month_label(int(value))
            elif key == TIME_ROW_TITLE:
                value = value.strftime('%d-%m-%Y')
            try:
                result_message += f"{key}: {int(value)}\n"
            except ValueError:
                result_message += f"{key}: {value}\n"
            except TypeError:
                result_message += f"{key}: {value}\n"
        else:
            continue
    return result_message
