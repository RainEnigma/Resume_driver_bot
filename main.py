from contextlib import closing
from data import texts_bot
import psycopg2
import telebot, datetime, logging.config
import data.datas, data
from data import exeptions
from telebot import types
import admin_conf
from database import creating_tab_count

import continue_working, thread_start_func, choose_city, choosing_time
from database import creating_table, delete_data
from data import config

# import cherrypy
#
# WEBHOOK_HOST = config.WEBHOOK_HOST
# WEBHOOK_PORT = 443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
# WEBHOOK_LISTEN = config.WEBHOOK_HOST  # На некоторых серверах придется указывать такой же IP, что и выше
#
# WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу
#
# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % (config.API_TOKEN)
#
# bot = telebot.TeleBot(config.API_TOKEN)
#
# # Наш вебхук-сервер
# class WebhookServer(object):
#     @cherrypy.expose
#     def index(self):
#         if 'content-length' in cherrypy.request.headers and \
#                 'content-type' in cherrypy.request.headers and \
#                 cherrypy.request.headers['content-type'] == 'application/json':
#             length = int(cherrypy.request.headers['content-length'])
#             json_string = cherrypy.request.body.read(length).decode("utf-8")
#             update = telebot.types.Update.de_json(json_string)
#             # Эта функция обеспечивает проверку входящего сообщения
#             bot.process_new_updates([update])
#             return ''
#         else:
#             raise cherrypy.HTTPError(403)


logging.config.fileConfig(fname='data/logging.conf')
logger = logging.getLogger(name="mainFunc")

bot = telebot.TeleBot(config.API_TOKEN, threaded=True)

logger.info("Program started")

creating_table.creating_tables_in_DB("driver")
creating_table.creating_tables_in_DB("passenger")
list_admins = [688033543, 238008205]


def func_del_messages(message, numb_of_messages):
    try:
        for num in range(numb_of_messages):
            bot.delete_message(message.chat.id, message.message_id - num)
    except Exception:
        pass


creating_tab_count.create_tab_count("users")


@bot.message_handler(commands=['help'])
def help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton("/start")
    markup.row(button_start)
    bot.send_message(message.chat.id,
                     texts_bot.text_help,
                     reply_markup=markup, parse_mode='html')


@bot.message_handler(commands=['start'])
def start(message):
    func_del_messages(message, 100)  # удаляем до 100 предидущих сообщений

    if message.from_user.id in list_admins:
        admin_conf.admin_conf(bot=bot, message=message)

    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_driver = types.InlineKeyboardButton(text="🚙 Водитель", callback_data="Водитель")
        button_passenger = types.InlineKeyboardButton(text="🚶‍♂ Пассажир", callback_data="Пассажир")
        markup.add(button_driver, button_passenger)

        # вывод сообщения над кнопками
        bot.send_message(message.chat.id,
                         f"Здравствуйте {message.from_user.first_name}!\n"
                         "Вас приветствует Бот-попутчик🚗!\n"
                         "Пожалуйста выберите категорию:\n",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'колличество людей' and message.from_user.id in list_admins:
        func_del_messages(message, 5)

        with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                      user=data.datas.user_DB,
                                      password=data.datas.password_DB,
                                      host=data.datas.host_DB)) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f"""SELECT numb FROM users""")
                answers_cur = cursor.fetchall()

        bot.send_message(message.from_user.id, f"🧞‍♂ нас уже - {answers_cur[-1][0]} чел.")
        start(message)

    if message.text == 'очистить экран' and message.from_user.id in list_admins:
        func_del_messages(message, 100)


# слушатель нажатых кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    markup_start_help = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_start_help.row('/start', '/help')
    if call.message:

        if call.data == 'okokok':
            bot.send_chat_action(call.message.chat.id, 'typing')
            func_del_messages(call.message, 2)
            start(call.message)

        # Если нажата кнопка водитель
        if call.data == "Водитель":
            bot.send_chat_action(call.message.chat.id, 'upload_video_note')
            func_del_messages(call.message, 10)

            if call.message.chat.username is None:
                img = open('data/settings_user_name.gif', 'rb')
                bot.send_document(call.message.chat.id, img)
                markup = types.InlineKeyboardMarkup(row_width=1)
                button_ok = types.InlineKeyboardButton(text="Мне все ясно 👌", callback_data="okokok")
                markup.add(button_ok)

                bot.send_message(call.message.chat.id,
                                 'В Вашем аккаунте не указано "имя пользователя" (Username). '
                                 'Имя пользвателя - единственный параметр по которому с Вами '
                                 'могут связаться пассажиры (при этом Ваш телефон не будет '
                                 'им доступен).\n'
                                 'Пожалуйста укажите имя пользователя в настройках телеграма.',
                                 reply_markup=markup)

            else:
                delete_data.delete_data(user_id=call.from_user.id,
                                        columt_to_change='user_id',
                                        tab_name='driver')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
                button_location = types.KeyboardButton("Передать свою геолокацию в "
                                                       "качестве начальной точки",
                                                       request_location=True)

                markup.row(button_location)
                markup.row('/start', '/help')

                message_id_to_del = bot.send_message(call.message.chat.id,
                                                     "Передайте свою геопозицию в качестве начальной точки - "
                                                     "соответствующая кнопка\n"
                                                     "или введите 🏙 город (ПГТ, село) начала маршрута.\n\n"
                                                     "❗️ВНИМАНИЕ❗ (при вводе вручную)️\n\n "
                                                     "неправильные запросы:\n "
                                                     "❌Киев, Жилянская 24\n "
                                                     "❌Святопетровское Леси украинки 2\n\n "
                                                     "правильные запросы:\n "
                                                     "✅Киев\n "
                                                     "✅Святопетровское",
                                                     reply_markup=markup).message_id

                bot.register_next_step_handler(call.message,
                                               choose_city.chose_city,
                                               'start',
                                               message_id_to_del,
                                               'driver',
                                               bot)

        if call.data == "Пассажир":
            try:
                for num in range(10):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                pass
            delete_data.delete_data(user_id=call.from_user.id,
                                    columt_to_change='user_id',
                                    tab_name='passenger')

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
            button_location = types.KeyboardButton("Передать свою геолокацию в "
                                                   "качестве начальной точки",
                                                   request_location=True)
            markup.row(button_location)
            markup.row('/start', '/help')

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Передайте свою геопозицию в качестве начальной точки - "
                                                 "соответствующая кнопка\n"
                                                 "или введите 🏙 город (ПГТ, село) начала маршрута.\n\n"
                                                 "❗️ВНИМАНИЕ❗ (при вводе вручную)️\n\n "
                                                 "неправильные запросы:\n "
                                                 "❌Киев, Жилянская 24\n "
                                                 "❌Святопетровское Леси украинки 2\n\n "
                                                 "правильные запросы:\n "
                                                 "✅Киев\n "
                                                 "✅Святопетровское",
                                                 reply_markup=markup).message_id

            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'start',
                                           message_id_to_del,
                                           'passenger',
                                           bot)
        # водитель ДА
        if call.data == "start_driver_point_yes":

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Замечательно, теперь введите 🏙 "
                                                 "город финальной точки:",
                                                 reply_markup=markup_start_help).message_id
            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in start_driver_point_yes message to delete not found")

            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'end',
                                           message_id_to_del,
                                           'driver',
                                           bot)
        # водитель НЕТ
        if call.data == "start_driver_point_no":
            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in start_driver_point_no message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Попробуйте ввести адрес повторно:\n"
                                                 "Введите 🏙 город начала маршрута:",
                                                 reply_markup=markup_start_help).message_id
            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'start',
                                           message_id_to_del,
                                           'driver',
                                           bot)

        # пассажир ДА
        if call.data == "start_passenger_point_yes":

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Замечательно, теперь введите 🏙 "
                                                 "город финальной точки:",
                                                 reply_markup=markup_start_help).message_id
            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id,
                                       call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in start_passenger_point_yes message to delete not found")

            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'end',
                                           message_id_to_del,
                                           'passenger',
                                           bot)

        # пассажир НЕТ
        if call.data == "start_passenger_point_no":
            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in start_passenger_point_no message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Попробуйте ввести адрес повторно:\n"
                                                 "Введите 🏙 город начала маршрута:",
                                                 reply_markup=markup_start_help).message_id
            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'start',
                                           message_id_to_del,
                                           'passenger',
                                           bot)

        # переходим к выбору даты Водителя

        if call.data == "end_driver_point_yes":
            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in end_driver_point_yes message to delete not found")

            markup = types.InlineKeyboardMarkup(row_width=2)
            button_today = types.InlineKeyboardButton(text="Сегодня",
                                                      callback_data="driver_today")
            button_tomorrow = types.InlineKeyboardButton(text="Завтра",
                                                         callback_data="driver_tomorrow")
            markup.add(button_today, button_tomorrow)
            bot.send_message(call.message.chat.id, "Прекрасно, когда едем?", reply_markup=markup)

        if call.data == "end_driver_point_no":

            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in end_driver_point_no message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Попробуйте ввести адрес повторно:\n"
                                                 "Введите 🏙 город финальной точки маршрута:",
                                                 reply_markup=markup_start_help).message_id
            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'end',
                                           message_id_to_del,
                                           'driver',
                                           bot)

        #     переходим к выбору даты Пассажира
        if call.data == "end_passenger_point_yes":

            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in end_passenger_point_yes message to delete not found")

            markup = types.InlineKeyboardMarkup(row_width=2)
            button_today = types.InlineKeyboardButton(text="Сегодня",
                                                      callback_data="passenger_today")
            button_tomorrow = types.InlineKeyboardButton(text="Завтра",
                                                         callback_data="passenger_tomorrow")
            markup.add(button_today, button_tomorrow)
            bot.send_message(call.message.chat.id, "Прекрасно, когда едем?", reply_markup=markup)

        if call.data == "end_passenger_point_no":

            try:
                for num in range(3):
                    bot.delete_message(call.message.chat.id, call.message.message_id - num)
            except Exception:
                logger.info(
                    f"USER - {call.message.chat.id} in end_passenger_point_no message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Попробуйте ввести адрес повторно:\n"
                                                 "Введите 🏙 город финальной точки маршрута:",
                                                 reply_markup=markup_start_help).message_id
            bot.register_next_step_handler(call.message,
                                           choose_city.chose_city,
                                           'end',
                                           message_id_to_del,
                                           'passenger',
                                           bot)

        #     переходим к выбору времени Водителя
        if call.data == "driver_today":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                logger.info(f"USER - {call.message.chat.id} in driver_today "
                            f"message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Теперь введите время\n"
                                                 "в формате 00:00").message_id
            my_time = datetime.datetime.now().strftime('%d.%m.%Y')
            bot.register_next_step_handler(call.message,
                                           choosing_time.chose_time,
                                           my_time, message_id_to_del,
                                           'driver',
                                           bot)

        if call.data == "driver_tomorrow":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                logger.info(f"USER - {call.message.chat.id} in driver_tomorrow "
                            f"message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Теперь введите время\n"
                                                 "в формате 00:00").message_id

            # находим завтрашнюю дату
            date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            my_time = date_tomorrow.strftime('%d.%m.%Y')

            bot.register_next_step_handler(call.message,
                                           choosing_time.chose_time,
                                           my_time,
                                           message_id_to_del,
                                           'driver',
                                           bot)

        #     переходим к выбору времени Пассажира
        if call.data == "passenger_today":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                logger.info(f"USER - {call.message.chat.id} in passenger_today "
                            f"message to delete not found")
            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Теперь введите время\n"
                                                 "в формате 00:00").message_id
            my_time = datetime.datetime.now().strftime('%d.%m.%Y')
            bot.register_next_step_handler(call.message,
                                           choosing_time.chose_time,
                                           my_time,
                                           message_id_to_del,
                                           'passenger',
                                           bot)

        if call.data == "passenger_tomorrow":

            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                logger.info(f"USER - {call.message.chat.id} in passenger_tomorrow "
                            f"message to delete not found")

            message_id_to_del = bot.send_message(call.message.chat.id,
                                                 "Теперь введите время\n"
                                                 "в формате 00:00").message_id

            # находим завтрашнюю дату
            date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            my_time = date_tomorrow.strftime('%d.%m.%Y')

            bot.register_next_step_handler(call.message,
                                           choosing_time.chose_time,
                                           my_time,
                                           message_id_to_del,
                                           'passenger',
                                           bot)


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except exeptions.Something_with_poling as e:
        print(f"bot_poling - {e}")

# # Снимаем вебхук перед повторной усgiтановкой (избавляет от некоторых проблем)
# bot.remove_webhook()
#
# # Ставим заново вебхук
# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))
#
# cherrypy.config.update({
#     'server.socket_host': WEBHOOK_LISTEN,
#     'server.socket_port': WEBHOOK_PORT,
#     'server.ssl_module': 'builtin',
#     'server.ssl_certificate': WEBHOOK_SSL_CERT,
#     'server.ssl_private_key': WEBHOOK_SSL_PRIV
# })
#
# cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
#
try:
    thread_start_func.set_interval(continue_working.continue_working, 5)
except Exception as e:
    logger.info(f"problem in passenger_search - {e}")
