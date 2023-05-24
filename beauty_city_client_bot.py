import telebot
from telebot import types
from environs import Env


env = Env()
env.read_env(override=True)
bot = telebot.TeleBot(env.str("TELEGRAM_CLIENT_BOT_API_TOKEN"))


# Приветствие и кнопка START
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    accept_button = types.InlineKeyboardButton("Принимаю", callback_data='main_menu')
    markup.add(accept_button)
    bot.send_message(message.chat.id, "Пользовательское соглашение и соглашение на обработку данных.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'main_menu': main_menu(call)
    if call.data == 'about': about(call)
    if call.data == 'choose_master': choose_master(call)
    if call.data == 'master_olga': choose_date_time(call.message, master='Ольга')
    if call.data == 'master_tatyana': choose_date_time(call.message, master='Татьяна')
    if call.data == 'choose_procedure': choose_procedure(call)


def main_menu(call):
    dialogue_text = 'Выберите пункт меню:'
    markup = types.InlineKeyboardMarkup(row_width=1)
    about_button = types.InlineKeyboardButton("О Нас", callback_data='about')
    choose_master_button = types.InlineKeyboardButton("Выбор мастера", callback_data='choose_master')
    choose_procedure_button = types.InlineKeyboardButton("Выбор процедуры", callback_data='choose_procedure')

    markup.add(about_button, choose_master_button, choose_procedure_button)
    bot.edit_message_text(dialogue_text, call.message.chat.id, call.message.id, reply_markup=markup)


def choose_master(call):
    dialogue_text = 'Выберите мастера:'
    markup = types.InlineKeyboardMarkup(row_width=2)
    olga_button = types.InlineKeyboardButton("Ольга", callback_data='master_olga')
    tatyana_button = types.InlineKeyboardButton("Татьяна", callback_data='master_tatyana')
    back_button = types.InlineKeyboardButton("Назад", callback_data='main_menu')

    markup.add(olga_button, tatyana_button, back_button)
    bot.edit_message_text(dialogue_text, call.message.chat.id, call.message.id, reply_markup=markup)


def choose_procedure(call):
    dialogue_text = 'Выберите процедуру:'
    markup = types.InlineKeyboardMarkup(row_width=2)
    procedure_1 = types.InlineKeyboardButton("Маникюр", callback_data='procedure_nails')
    procedure_2 = types.InlineKeyboardButton("Массаж", callback_data='procedure_massage')
    back_button = types.InlineKeyboardButton("Назад", callback_data='main_menu')

    markup.add(procedure_1, procedure_2, back_button)
    bot.edit_message_text(dialogue_text, call.message.chat.id, call.message.id, reply_markup=markup)


def choose_date_time(message, master):
    # Ваш код для выбора даты и времени
    # ...

    # Пример вывода сообщения с выбором даты и времени
    bot.send_message(message.chat.id, f"Выбран мастер: {master}. Теперь выберите дату и время для записи.")
    # Здесь вы можете добавить функционал для выбора даты и времени, например, с использованием InlineKeyboardMarkup
    # ...


def successful_booking(message, details):
    bot.send_message(message.chat.id, f"Поздравляем с успешной записью! Вот детали вашей записи:\n\n{details}")

    # Ваш код для обработки успешной записи


# Добавление кнопки "позвонить нам" в ReplyKeyboardMarkup
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == "позвонить нам":
        bot.send_message(message.chat.id, "Рады звонку в любое время – 8 800 555 35 35")
    else:
        bot.send_message(message.chat.id, "Выберите действие из меню или введите 'позвонить нам', чтобы связаться с нами.")


if __name__ == '__main__':
    bot.infinity_polling()
