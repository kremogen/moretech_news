import json
import sqlite3
import enum

import telebot
from telebot import types

bot = telebot.TeleBot('5684608047:AAFa-ki6eE395VkatiMJMPIsHItLpJHLdjE')
user_actions = dict()


class UserAction(enum.Enum):
    WAITING_FOR_ROLE_NAME = 0
    WAITING_FOR_CUSTOM_WORDS = 1


@bot.message_handler(content_types=['text'])
def start(message):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE id = ?', (message.from_user.id,))
    id = cursor.fetchone()
    conn.close()

    if message.text == '/start':
        try:
            if id is None:
                send_startup(message.from_user.id)
            else:
                if get_user_role(message.from_user.id) is None:
                    send_role_choose(message.from_user.id)
                else:
                    send_main_menu(message.from_user.id)

        except Exception as e:
            print(e)
    else:
        if id is None:
            send_startup(message.from_user.id)
            return

        if message.from_user.id in user_actions.keys():
            if user_actions[message.from_user.id] == UserAction.WAITING_FOR_ROLE_NAME:
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET custom_role = ? WHERE id = ?',
                               [message.text, message.from_user.id])
                conn.commit()
                conn.close()
                del user_actions[message.from_user.id]
            elif user_actions[message.from_user.id] == UserAction.WAITING_FOR_CUSTOM_WORDS:
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                sp = message.text.split(', ')
                cursor.execute('UPDATE users SET custom_words = ? WHERE id = ?',
                               [json.dumps(sp), message.from_user.id])
                conn.commit()
                conn.close()
                del user_actions[message.from_user.id]

        send_main_menu(message.from_user.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'startup':
        send_role_choose(call.from_user.id)
    elif call.data == 'back':
        send_main_menu(call.from_user.id)
    elif call.data == 'buh':
        update_user_role(call.from_user.id, 'buh')
        send_main_menu(call.from_user.id)
    elif call.data == 'dir':
        update_user_role(call.from_user.id, 'dir')
        send_main_menu(call.from_user.id)
    elif call.data == 'another':
        bot.send_message(call.message.chat.id, '📎 Напишите краткое описание вашей деятельности (1-2 слова):')
        update_user_role(call.from_user.id, 'another')
        user_actions[call.from_user.id] = UserAction.WAITING_FOR_ROLE_NAME
    elif call.data == 'key_words':
        bot.send_message(call.message.chat.id, f'📌 Укажите список слов, который '
                                               f'может охарактеризовать вашу деятельность:')
        user_actions[call.from_user.id] = UserAction.WAITING_FOR_CUSTOM_WORDS
    elif call.data == 'trending':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(call.message.chat.id, 'Trending news', reply_markup=keyboard)
    elif call.data == 'insights':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(call.message.chat.id, 'Insights', reply_markup=keyboard)
    elif call.data == 'digests':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(call.message.chat.id, 'Digests', reply_markup=keyboard)


def send_startup(id: int):
    create_user_profile(id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Продолжить', callback_data='startup'))
    bot.send_message(id,
                     f'🤖 Привет, я специально обученный Бот для выдачи самых интересных и свежих новостей в мире '
                     f'бизнеса.\n\n📚 Мои алгоритмы позволяют выбрать самые релевантные новости, исходя из твоих интересесов '
                     f'в той или иной сфере.\n\n👉 Ну что, приступим?!',
                     reply_markup=keyboard)


def get_user_role(id: int) -> str or None:
    conn2 = sqlite3.connect("users.db")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT role FROM users WHERE id = ?', (id,))
    role = cursor2.fetchone()
    conn2.close()
    return role


def get_user_custom_words(id: int) -> dict or None:
    conn2 = sqlite3.connect("users.db")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT custom_words FROM users WHERE id = ?', (id,))
    words = cursor2.fetchone()
    conn2.close()
    return json.loads(words[0]) if words[0] is not None else None


def get_custom_user_role(id: int):
    conn2 = sqlite3.connect("users.db")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT custom_role FROM users WHERE id = ?', (id,))
    role = cursor2.fetchone()
    conn2.close()
    return role


def send_role_choose(id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Управление бизнесом', callback_data='dir'))
    keyboard.add(types.InlineKeyboardButton(text='Бухгалтерия', callback_data='buh'))
    keyboard.add(types.InlineKeyboardButton(text='Другое', callback_data='another'))
    bot.send_message(id, '🕺 Выберите пункт, который наилучшим образом описывает вашу деятельность:',
                     reply_markup=keyboard)


def send_main_menu(id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='📈 В тренде!', callback_data='trending'))
    keyboard.add(types.InlineKeyboardButton(text='📊 Инсайты', callback_data='insights'))
    keyboard.add(types.InlineKeyboardButton(text='📝 Дайджесты', callback_data='digests'))
    keyboard.add(types.InlineKeyboardButton(text='Сменить интересы', callback_data='startup'))

    role_name = get_user_role(id)[0]
    if role_name == 'dir':
        role_name = 'Управление бизнесом'
    elif role_name == 'buh':
        role_name = 'Бухгалтерия'
    elif role_name == 'another':
        role_name = get_custom_user_role(id)[0]
        words = get_user_custom_words(id)

        keyboard.add(types.InlineKeyboardButton(text='Изменить ключевые слова', callback_data='key_words'))
        bot.send_message(id,
                         f'📌 Вас интересует: {str(role_name)}\n Ключевые слова: '
                         f'{("Не заданы" if words is None else ", ".join(words))}'
                         f'\n\nВыберите пункт для получения сводки:',
                         reply_markup=keyboard)
        return
    else:
        # todo: maybe NPE
        pass

    bot.send_message(id, f'📌 Вас интересует: {str(role_name)}\n\nВыберите пункт для получения сводки:',
                     reply_markup=keyboard)


def create_user_profile(id: int) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id) VALUES (?)', [id])
    conn.commit()
    conn.close()


def update_user_role(id: int, role: str) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', [role, id])
    conn.commit()
    conn.close()


def init_db():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        cursor.close()
        conn.close()
        print('База данных найдена, начинаю работу!')
    except Exception:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            'CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL, role TEXT DEFAULT NULL, custom_role TEXT DEFAULT NULL, custom_words TEXT DEFAULT NULL)'
        )
        conn.commit()
        conn.close()
        print('База данных не найдена, создаю и начинаю работу!')


if __name__ == '__main__':
    init_db()
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(e)
