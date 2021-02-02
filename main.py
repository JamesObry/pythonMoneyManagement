import telebot
import sqlite3 as sq
from telebot import types

with sq.connect("money.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS money (
        id INTEGER PRIMARY KEY,
        balance REAL
    )""")

bot = telebot.TeleBot('1509447385:AAGmakl6_pkqxZXlj4YpMbd__cpRevlWeoQ')

# keyboards
main = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
mainMoney = types.KeyboardButton(text='Обновить баланс 💸')
mainStats = types.KeyboardButton(text='Мой баланс 🤑')
mainRemoveMoney = types.KeyboardButton(text='Очистить баланс')
main.add(mainMoney, mainStats, mainRemoveMoney)

accept = types.InlineKeyboardMarkup()
acceptYes = types.InlineKeyboardButton(text='Да, я уверен', callback_data='yes')
acceptNo = types.InlineKeyboardButton(text='Нет, я передумал', callback_data='no')
accept.add(acceptYes, acceptNo)

@bot.message_handler(commands=['start'])
def startMessagae(message):
    try:
        with sq.connect("money.db") as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO money(id, balance) VALUES ({message.chat.id}, 0)")
            bot.send_message(message.chat.id, 'Регистрация успешна!\nТы можешь записывать сюда свои доходы.\nИспользуй клавиатуру для навигации!', reply_markup=main)
    except:
        bot.send_message(message.chat.id, 'Авторизация успешна!\nЗапиши какую суммы та заработал пока тебя небыло.', reply_markup=main)

@bot.message_handler(regexp='Обновить баланс 💸')
def money(message):
    bot.send_message(message.chat.id, 'Укажы какую сымму ты заработал? 💸 ( в долларах )')
    bot.register_next_step_handler(message, m)
def m(message):
    newBalance = message.text
    try:
        with sq.connect("money.db") as con:
            cur = con.cursor()
            cur.execute(f"UPDATE money SET balance = balance + {newBalance} WHERE id = {message.chat.id}")
            balance = cur.execute(f"SELECT balance FROM money WHERE id = {message.chat.id}")
            balance = cur.fetchone()[0]
            bot.send_message(message.chat.id, f'Успешно! 🤑 Твой баланс уже составляет целых: {balance} 💵')
    except:
        bot.send_message(message.chat.id, 'Что-то пошло не так... 🚫 Нам не удалось обновить твой баланс... Попробуй еще раз.')

@bot.message_handler(regexp='Мой баланс 🤑')
def myBalance(message):
    with sq.connect("money.db") as con:
        cur = con.cursor()
        balance = cur.execute(f"SELECT balance FROM money WHERE id = {message.chat.id}")
        balance = cur.fetchone()[0]
        bot.send_message(message.chat.id, f'🤑 Твой баланс уже составляет целых: {balance} 💵')

@bot.message_handler(regexp='Очистить баланс')
def removeMoney(message):
    with sq.connect("money.db") as con:
        cur = con.cursor()
        balance = cur.execute(f"SELECT balance FROM money WHERE id = {message.chat.id}")
        balance = cur.fetchone()[0]
        bot.send_message(message.chat.id, f'Ты действительно уверен что хочешь обновить свой баланс в {balance} 💵', reply_markup=accept)

@bot.callback_query_handler(func=lambda call:True)
def check(call):
    if call.data == 'yes':
        with sq.connect("money.db") as con:
            cur = con.cursor()
            cur.execute(f"UPDATE money SET balance = 0 WHERE id = {call.message.chat.id}")
            balance = cur.execute(f"SELECT balance FROM money WHERE id = {call.message.chat.id}")
            balance = cur.fetchone()[0]
            bot.send_message(call.message.chat.id, 'Твой баланс был успешно обнулен.')
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Твой баланс не был изменен.')

bot.infinity_polling(True)