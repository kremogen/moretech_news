import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('5684608047:AAFa-ki6eE395VkatiMJMPIsHItLpJHLdjE')


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute('SELECT `id` FROM users WHERE id = ?', (message.from_user.id,))
            id = cursor.fetchone()
            cursor.close()
            conn.close()

            if id is None:
                create_user_profile(message.from_user.id)
            else:
                pass

            # keyboard = types.InlineKeyboardMarkup()
            # key_buh = types.InlineKeyboardButton(text='Бухгалтер', callback_data='buh')
            # keyboard.add(key_buh)
            # key_dir = types.InlineKeyboardButton(text='Директор', callback_data='dir')
            # keyboard.add(key_dir)
            #
            # conn2 = sqlite3.connect("users.db")
            # cursor2 = conn2.cursor()
            # cursor2.execute('SELECT role FROM users WHERE id = ?', (message.from_user.id,))
            # role = cursor2.fetchone()
            # cursor2.close()
            # conn2.close()
            #
            # if role is not None:
            #     key_other = types.InlineKeyboardButton(text=str(role), callback_data=str(role))
            #     keyboard.add(key_other)
            # else:

            key_other = types.InlineKeyboardButton(text='Другая роль', callback_data='another')
            keyboard.add(key_other)
            bot.send_message(message.from_user.id,
                             'Привет, я бот MoreTechNews\n\nЯ подберу для тебя самые релевантные новости исходя из '
                             'выбранной роли\n\nУкажи, какая роль тебе подходит больше всего',
                             reply_markup=keyboard)
        except Exception as e:
            print(e)

            keyboard = types.InlineKeyboardMarkup()
            key_buh = types.InlineKeyboardButton(text='Бухгалтер', callback_data='buh')
            keyboard.add(key_buh)
            key_dir = types.InlineKeyboardButton(text='Директор', callback_data='dir')
            keyboard.add(key_dir)
            key_other = types.InlineKeyboardButton(text='Другая', callback_data='another')
            keyboard.add(key_other)
            bot.send_message(message.from_user.id,
                             'Привет, я бот MoreTechNews\n\nБот подберёт для тебя самые релевантные новости исходя из выбранной роли\n\nУкажи, какая роль тебе подходит больше всего',
                             reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "buh":
        bot.send_message(call.message.chat.id, 'Брух чел')
    elif call.data == "dir":
        bot.send_message(call.message.chat.id, 'Дир чел')
    elif call.data == "another":
        bot.send_message(call.message.chat.id, 'Укажите название роли, которую хотите добавить:')


def create_user_profile(id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (`id`) VALUES (?)', [id])
    conn.commit()
    conn.close()
    cursor.close()


def init_db():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        cursor.close()
        conn.close()
        print('База данных найдена, начинаю работу!')
    except Exception as e:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            'CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL, role TEXT DEFAULT NULL, key_words TEXT DEFAULT NULL)')
        conn.commit()
        conn.close()
        print('База данных не найдена, создаю и начинаю работу!')


if __name__ == '__main__':
    init_db()
    bot.polling(none_stop=True, interval=0)
