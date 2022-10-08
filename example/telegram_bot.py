import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('5684608047:AAFa-ki6eE395VkatiMJMPIsHItLpJHLdjE')
waiting_another = []


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute('SELECT `id` FROM users WHERE id = ?', (message.from_user.id,))
            id = cursor.fetchone()
            conn.close()

            if id is None:
                create_user_profile(message.from_user.id)
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text='Продолжить', callback_data='startup'))
                bot.send_message(message.from_user.id,
                                 'Привет, я бот MoreTechNews\n\nЯ подберу для тебя самые релевантные новости исходя из '
                                 'выбранной роли\n\nПриступим?',
                                 reply_markup=keyboard)
            else:
                if get_user_role(message.from_user.id) is None:
                    send_role_choose(message.from_user.id)
                else:
                    send_main_menu(message.from_user.id)
        except Exception as e:
            print(e)
    else:
        if message.from_user.id in waiting_another:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET `custom_role` = ? WHERE `id` = ?', [message.text, message.from_user.id])
            conn.commit()
            conn.close()
            waiting_another.remove(message.from_user.id)

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
        bot.send_message(call.message.chat.id, 'Укажите название роли, которую хотите добавить:')
        update_user_role(call.from_user.id, 'another')
        waiting_another.append(call.from_user.id)
    elif call.data == 'key_words':
        send_main_menu(call.from_user.id)

        # todo: generate news block
    elif call.data == 'trending':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        bot.send_message(call.message.chat.id, 'Trending news', reply_markup=keyboard)


def get_user_role(id: int):
    conn2 = sqlite3.connect("users.db")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT role FROM users WHERE id = ?', (id,))
    role = cursor2.fetchone()
    conn2.close()
    return role


def get_custom_user_role(id: int):
    conn2 = sqlite3.connect("users.db")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT custom_role FROM users WHERE id = ?', (id,))
    role = cursor2.fetchone()
    conn2.close()
    return role


def send_role_choose(id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Бухгалтер', callback_data='buh'))
    keyboard.add(types.InlineKeyboardButton(text='Директор', callback_data='dir'))
    keyboard.add(types.InlineKeyboardButton(text='Другая', callback_data='another'))
    bot.send_message(id, 'Укажите, какая роль подходит вам больше всего', reply_markup=keyboard)


def send_main_menu(id: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Тренды', callback_data='trending'))
    keyboard.add(types.InlineKeyboardButton(text='Сменить роль', callback_data='startup'))

    role_name = get_user_role(id)[0]
    if role_name == 'dir':
        role_name = 'Директор'
    elif role_name == 'buh':
        role_name = 'Бухгалтер'
    elif role_name == 'another':
        role_name = get_custom_user_role(id)[0]
        keyboard.add(types.InlineKeyboardButton(text='Изменить ключевые слова', callback_data='key_words'))
    else:
        # todo: maybe NPE
        pass

    bot.send_message(id, f'Ваша роль: {str(role_name)}\n\nВыберите интересующий вас пункт:',
                     reply_markup=keyboard)


def create_user_profile(id: int) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (`id`) VALUES (?)', [id])
    conn.commit()
    conn.close()


def update_user_role(id: int, role: str) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET `role` = ? WHERE `id` = ?', [role, id])
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
    bot.polling(none_stop=True, interval=0)
