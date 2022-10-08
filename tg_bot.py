import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('5684608047:AAFa-ki6eE395VkatiMJMPIsHItLpJHLdjE')

try:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    conn.close()
    print('База данных найдена, начинаю работу!')
except Exception:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id integer, role text, keys text)')
    conn.commit()
    conn.close()
    print('База данных не найдена, создаю и начинаю работу!')

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s' % message.from_user.id)
            cursor.close()
            conn.close()
            keyboard = types.InlineKeyboardMarkup()
            key_buh = types.InlineKeyboardButton(text='Бухгалтер', callback_data='buh')
            keyboard.add(key_buh)
            key_dir = types.InlineKeyboardButton(text='Директор', callback_data='dir')
            keyboard.add(key_dir)
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            [role], = cursor.execute('SELECT role FROM users WHERE id = %s' % message.from_user.id)
            conn.close()
            if str(role).strip():
                key_other = types.InlineKeyboardButton(text=str(role), callback_data=str(role))
                keyboard.add(key_other)
            else:
                key_other = types.InlineKeyboardButton(text='Другая роль', callback_data='another')
                keyboard.add(key_other)
            bot.send_message(message.from_user.id,
                            'Привет, я бот MoreTechNews\n\nЯ подберу для тебя самые релевантные новости исходя из выбранной роли\n\nУкажи, какая роль тебе подходит больше всего',
                            reply_markup=keyboard)
        except Exception as e:
            print(e)
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            insert = [message.from_user.id, '', '']
            cursor.execute('INSERT INTO users VALUES (?, ?, ?)', insert)
            conn.commit()
            conn.close()
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
    if message.text == 'Другая':
        pass



@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "buh":
        bot.send_message(call.message.chat.id, 'Брух чел')
    elif call.data == "dir":
        bot.send_message(call.message.chat.id, 'Дир чел')
    elif call.data == "another":
        bot.send_message(call.message.chat.id, 'Укажите название роли, которую хотите добавить:')


bot.polling(none_stop=True, interval=0)
