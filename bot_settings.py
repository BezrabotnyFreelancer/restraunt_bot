from enum import Enum


class Parms(Enum):
    message_limit = 1
    collection = 2
    messages = 3
    buttons = 4
    menu = 5
    parse_mode = 6
    top_buttons_range = 7
    top_messages_range = 8
    top_users_range = 9
    time_range = 10


DATABASE = {
    Parms.collection: 'cafe_telebot',
    Parms.messages: 'messages',
    Parms.buttons: 'buttons',
    Parms.menu: 'menu',
}

SETTINGS = {
    Parms.message_limit: 1000,
    Parms.parse_mode: 'html',
    Parms.top_buttons_range: 5,
    Parms.top_messages_range: 5,
    Parms.top_users_range: 10,
    Parms.time_range: 10
}
