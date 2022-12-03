from bot_exceptions import EmptyResult
from firestore_client import FirestoreClient
from datetime import datetime, timedelta
from create_menu import MenuInfo, MENU_DIR
from bot_settings import DATABASE, SETTINGS, Parms
from enum import Enum


class Dirs(Enum):
    button_taps = 1
    user_buttons = 2
    user_messages = 3


dirs = {
    Dirs.button_taps: 'button_taps',
    Dirs.user_buttons: 'user_buttons',
    Dirs.user_messages: 'user_messages'
}


def get_menu_data(client: FirestoreClient, menu_title: str):
    return client.get_document(DATABASE[Parms.collection], DATABASE[Parms.menu])[menu_title]


def get_top(document: dict, field: str):
    res = {}
    for user in document:
        for data in document[user]:
            key = data[field]
            if key not in res:
                res[key] = 1
            else:
                res[key] += 1
    return sorted(res, key=lambda x: res[x], reverse=True)


def get_sorted_data_by_time(document: dict, date: datetime.date):
    res = {}
    for user in document:
        res[user] = list(filter(lambda x: x['date'].date() >= date, document[user]))
    return res


def get_top_users(document: dict):
    users = {data: len(document[data]) for data in document}
    return sorted(users, key=lambda x: users[x], reverse=True)


def get_top_buttons(client: FirestoreClient):
    document = client.get_document(DATABASE[Parms.collection], DATABASE[Parms.buttons])
    date = datetime.now().date() - timedelta(SETTINGS[Parms.time_range])
    sorted_by_time = get_sorted_data_by_time(document, date)
    taps = get_top(document, 'button')
    users = get_top_users(document)
    return {dirs[Dirs.button_taps]: taps, dirs[Dirs.user_buttons]: users}


def get_top_messages(client: FirestoreClient):
    document = client.get_document(DATABASE[Parms.collection], DATABASE[Parms.messages])
    users = get_top_users(document)
    return {dirs[Dirs.user_messages]: users}


def get_top_users_by_time(client: FirestoreClient):
    date = datetime.now().date() - timedelta(SETTINGS[Parms.time_range])
    messages = client.get_document(DATABASE[Parms.collection], DATABASE[Parms.messages])
    buttons = client.get_document(DATABASE[Parms.collection], DATABASE[Parms.buttons])
    sorted_messages = get_sorted_data_by_time(messages, date)
    sorted_buttons = get_sorted_data_by_time(buttons, date)
    top_buttons_by_time = get_top(sorted_buttons, 'button')
    top_users_by_msg = get_top_users(sorted_messages)
    top_users_by_btn = get_top_users(sorted_buttons)
    return {dirs[Dirs.user_messages]: top_users_by_msg,
            dirs[Dirs.user_buttons]: top_users_by_btn,
            dirs[Dirs.button_taps]: top_buttons_by_time}


def create_or_update_doc_data(client: FirestoreClient, doc_name: str,  field: str, data: dict):
    try:
        document = client.get_document(DATABASE[Parms.collection], doc_name)
        if document == {} or document is None:
            raise EmptyResult('Пустой документ')
    except EmptyResult:
        client.set_document(DATABASE[Parms.collection], doc_name, {field: [data]})
        return
    if field not in document:
        client.update_document(DATABASE[Parms.collection], doc_name, {field: [data]})
        return
    return document


def get_menu_position(lst: list or tuple, id: int):
    for i in lst:
        if i[MENU_DIR[MenuInfo.id]] == id:
            return i
    raise ValueError('Кнопка отсутствует')


def add_msg_in_db(message_text: str, date: datetime):
    return {'message': message_text, 'date': date}


def add_button_press_in_db(button_name: str, date: datetime):
    return {'button': button_name, 'date': date}


def generate_message(button: dict):
    msg = ''
    if MENU_DIR[MenuInfo.size] in button or MENU_DIR[MenuInfo.price] in button:
        msg += f'<b>Блюдо: {button[MENU_DIR[MenuInfo.name]]}\n</b>'
    if MENU_DIR[MenuInfo.size] in button:
        msg += f'<b>Размер порции: {button[MENU_DIR[MenuInfo.size]]}г.\n\n</b>'
    msg += button[MENU_DIR[MenuInfo.description]] + '\n'

    if MENU_DIR[MenuInfo.price] in button:
        msg += '\n\n'
        msg += f'<b>Цена: {button[MENU_DIR[MenuInfo.price]]} BYN</b>'

    return msg


def generate_rating_message(lst, title, rng, time=None):
    medals = ['🥇', '🥈', '🥉']
    if time is None:
        msg = f'<b>Топ {title}:</b> \n'
    else:
        msg = f'<b>Топ {title} за последние {SETTINGS[Parms.time_range]} дней:</b> \n'
    if len(lst) >= 3:
        msg += f"{medals[0]}{lst[0]}\n"
        msg += f"{medals[1]}{lst[1]}\n"
        msg += f"{medals[2]}{lst[2]}\n"
        msg += '\n'.join([' '*6 + x for x in lst[3:rng]])
    else:
        for i in range(len(lst)):
            msg += f"{medals[i]}{lst[i]}\n"
    return msg
