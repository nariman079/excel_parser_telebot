from src.config import DEADLINE_TITLE


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
                value = str(int(value)) + ' месяцев'
            try:
                result_message += f"{key}: {int(value)}\n"
            except ValueError:
                result_message += f"{key}: {value}\n"
            except TypeError:
                result_message += f"{key}: {value}\n"
        else:
            continue
    return result_message



