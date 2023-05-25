import datetime
import telebot
from telebot import types
from environs import Env


env = Env()
env.read_env(override=True)
bot = telebot.TeleBot(env.str("TELEGRAM_CLIENT_BOT_API_TOKEN"))

EMPTY_CACHE = {
    'first_time': True,
    'office': False,
    'master': False,
    'service': False,
    'date': False,
    'time': False,
    'phone': False,
    'last_message_id': False
    }

TIMES = [
    '10:00', '10:30',
    '11:00', '11:30',
    '12:00', '12:30',
    '13:00', '13:30',
    '14:00', '14:30',
    '15:00', '15:30',
    '16:00', '16:30',
    '17:00', '17:30',
    '18:00', '18:30',
    '19:00', '19:30',
    '20:00', '20:30'
]

MASTERS = {
    1: {'id': 1, 'name': 'Ольга', 'procedure': 'Стрижка/укладка волос'},
    2: {'id': 2, 'name': 'Татьяна', 'procedure': 'Макияж'}
}


# Приветствие и кнопка START
@bot.message_handler(commands=['start'])
def start_menu(message):
    if 'users' not in bot.__dict__.keys():
        bot.__dict__.update({'users': {}})
        bot.__dict__['users'].update({message.from_user.id: EMPTY_CACHE})

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(text='📞 Позвонить нам'))
    bot.send_message(message.chat.id, 'Добро пожаловать в BeautyCity!!!', reply_markup=markup)

    dialogue_text = 'Выберите пункт меню:'
    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    about_button = types.InlineKeyboardButton("О Нас", callback_data='about')
    choose_master_button = types.InlineKeyboardButton("Выбор мастера", callback_data='choose_master')
    choose_procedure_button = types.InlineKeyboardButton("Выбор процедуры", callback_data='choose_procedure')

    markup_inline.add(about_button, choose_master_button, choose_procedure_button)
    bot.send_message(message.chat.id, dialogue_text, reply_markup=markup_inline)


def main_menu(message):
    user_data = bot.__dict__['users'][message.chat.id]
    dialogue_text = 'Выберите пункт меню:'
    markup = types.InlineKeyboardMarkup(row_width=1)
    about_button = types.InlineKeyboardButton("О Нас", callback_data='about')
    choose_master_button = types.InlineKeyboardButton("Выбор мастера", callback_data='choose_master')
    choose_procedure_button = types.InlineKeyboardButton("Выбор процедуры", callback_data='choose_procedure')
    send_feedback_button = types.InlineKeyboardButton("Оставить отзыв о последнем посещении", callback_data='send_feedback')

    markup.add(about_button, choose_master_button, choose_procedure_button)
    if not user_data['first_time']:
        markup.add(send_feedback_button)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(call.data)

    if 'users' not in bot.__dict__.keys():      # Если сервер перезапускался, то клиент вернётся на стартовую страницу
        bot.__dict__.update({'users': {}})
        bot.__dict__['users'].update({call.message.chat.id: EMPTY_CACHE})
        start_menu(call.message)

    args = call.data.split('#')
    if call.data == 'main_menu': main_menu(call.message)
    if call.data == 'about': about(call.message)
    if call.data == 'choose_master': choose_master(call.message)
    if call.data.startswith('master'): choose_date(call.message, int(args[1]))
    if call.data.startswith('choose_date_back'): choose_date(call.message)
    if call.data.startswith('choose_time'): choose_time(call.message, args[1])

    if call.data == 'confirmation':
        confirmation(call.message, args[1])

    if call.data.startswith('successful_booking'): successful_booking(call.message)

    if call.data == 'choose_procedure': choose_procedure(call.message)


def about(message):
    dialogue_text = 'Студия BeautyCity' + '\n'
    dialogue_text += 'Instagram: @BeautyCity' + '\n'
    dialogue_text += 'Vkontakte: vk.com/BeautyCity' + '\n'

    markup = types.InlineKeyboardMarkup(row_width=1)
    button_1 = types.InlineKeyboardButton("Посетить сайт - beautycity.ru", url='https://www.beautycity.ru')
    button_back = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')

    markup.add(button_1, button_back)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_master(message):
    dialogue_text = 'Выберите мастера:'
    markup = types.InlineKeyboardMarkup(row_width=2)
    master_button_1 = types.InlineKeyboardButton("Ольга", callback_data='master#1')
    master_button_2 = types.InlineKeyboardButton("Татьяна", callback_data='master#2')
    button_back = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')

    markup.add(master_button_1, master_button_2, button_back)
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_procedure(call):
    dialogue_text = 'Выберите процедуру:'
    markup = types.InlineKeyboardMarkup(row_width=2)
    procedure_1 = types.InlineKeyboardButton("Маникюр", callback_data='procedure#1')
    procedure_2 = types.InlineKeyboardButton("Массаж", callback_data='procedure#2')
    button_back = types.InlineKeyboardButton('<< Назад', callback_data='main_menu')

    markup.add(procedure_1, procedure_2, button_back)
    bot.edit_message_text(dialogue_text, call.message.chat.id, call.message.id, reply_markup=markup)


def choose_date(message, master=None):

    user_data = bot.__dict__['users'][message.chat.id]
    if master:
        user_data.update({'master': master})
    else:
        master = user_data['master']

    buttons = []
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    today = datetime.datetime.now().date()
    days_to_end_of_next_week = 14 - today.weekday()

    for i in range(days_to_end_of_next_week):
        new_date = today + datetime.timedelta(days=i)
        formatted_date = f"{new_date.day:02d}.{new_date.month:02d} ({days[new_date.weekday()]})"
        buttons.append(types.InlineKeyboardButton(formatted_date, callback_data=f'choose_time#{formatted_date}'))

    dialogue_text = f'Вы записываетесь к мастеру: {MASTERS[master]["name"]}' + '\n'
    dialogue_text += f'Услуга: {MASTERS[master]["procedure"]}' + '\n'
    dialogue_text += '\nВыберите удобный Вам день:'

    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(buttons), 3):
        markup.add(*buttons[i:i+3])
    markup.row(types.InlineKeyboardButton('<< Назад', callback_data='choose_master'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def choose_time(message, date=None):

    user_data = bot.__dict__['users'][message.chat.id]
    if date:
        user_data.update({'date': date})
    else:
        date = user_data['date']

    dialogue_text = f'Вы записываетесь к мастеру: {MASTERS[user_data["master"]]["name"]}' + '\n'
    dialogue_text += f'Услуга: {MASTERS[user_data["master"]]["procedure"]}' + '\n'
    dialogue_text += f'Выбран день: {user_data["date"]}' + '\n'
    dialogue_text += '\nВыберите доступное время:'

    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for item in TIMES:
        buttons.append(types.InlineKeyboardButton(item, callback_data=f'confirmation#{item}'))

    for i in range(0, len(buttons), 4):
        markup.add(*buttons[i:i+4])
    markup.row(types.InlineKeyboardButton('<< Назад', callback_data='choose_date_back'))
    bot.edit_message_text(dialogue_text, message.chat.id, message.id, reply_markup=markup)


def confirmation(message, time=None):

    print(message)

    user_data = bot.__dict__['users'][message.chat.id]
    if time:
        user_data.update({'time': time})
        user_data.update({'last_message_id':message.id})
    else:
        time = user_data['time']

    dialogue_text = f'Вы записываетесь к мастеру: {MASTERS[user_data["master"]]["name"]}' + '\n'
    dialogue_text += f'Услуга: {MASTERS[user_data["master"]]["procedure"]}' + '\n'
    dialogue_text += f'Дата: {user_data["date"]}' + '\n'
    dialogue_text += f'Время: {user_data["time"]}' + '\n\n'

    if user_data['first_time']:
        print('True')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.row(types.InlineKeyboardButton('<< Назад', callback_data='choose_time#'))
        dialogue_text += 'Отправьте в чат, свой контактный номер.\n\n'
        dialogue_text += 'Отправляя нам свой телефон, Вы подтверждаете своё согласие на обработку Ваших данных.\n'
        dialogue_text += 'Более подробно с текстом соглашения можно ознакомиться по ссылке: www.confirmation.ru'
        bot.edit_message_text(dialogue_text, message.chat.id, reply_markup=markup)
        bot.register_next_step_handler(message, get_phone)
    else:
        print('Not_First')


def successful_booking(message):
    user_data = bot.__dict__['users'][message.chat.id]
    dialogue_text = f'Поздравляем с успешной записью!'
    dialogue_text = f'Мастер: {MASTERS[user_data["master"]]["name"]}' + '\n'
    dialogue_text += f'Услуга: {MASTERS[user_data["master"]]["procedure"]}' + '\n'
    dialogue_text += f'Дата: {user_data["date"]}' + '\n'
    dialogue_text += f'Время: {user_data["time"]}' + '\n'
    dialogue_text += f'Ваш номер для связи: {user_data["time"]}' + '\n'
    bot.send_message(message.chat.id, dialogue_text)
    start_menu(message)


# Добавление кнопки "позвонить нам" в ReplyKeyboardMarkup
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if "позвонить нам" in message.text.lower():
        bot.send_message(message.chat.id, "Рады звонку в любое время – 8 800 555 35 35")
    else:
        bot.send_message(message.chat.id, "Выберите действие из меню или введите 'позвонить нам', чтобы связаться с нами.")


def get_phone(message):
    user_data = bot.__dict__['users'][message.chat.id]
    user_data.update({'phone': message.text})

    dialogue_text = f'Вы записываетесь к мастеру: {MASTERS[user_data["master"]]["name"]}' + '\n'
    dialogue_text += f'Услуга: {MASTERS[user_data["master"]]["procedure"]}' + '\n'
    dialogue_text += f'Дата: {user_data["date"]}' + '\n'
    dialogue_text += f'Время: {user_data["time"]}' + '\n'
    dialogue_text += f'Контактный телефон: {message.text}' + '\n\n'
    dialogue_text += f'Подтвердите запись, или введите другой телефон для связи'

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.row(types.InlineKeyboardButton('Подтвердить Запись', callback_data='choose_time#'))
    markup.row(types.InlineKeyboardButton('<< Назад', callback_data='choose_time#forgot_phone'))


if __name__ == '__main__':
    bot.infinity_polling()
