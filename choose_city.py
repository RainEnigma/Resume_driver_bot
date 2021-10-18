from database import adding_user_id, working_with_db
from geopy.geocoders import Nominatim, GeocodeEarth
import apply_chosen_address
import chosing_street
import main
from add_statistics import adding_stat
from telebot import types


def chose_city(message, argum, message_id_to_del, arg_role, bot):
    # получение id пользователя и передача его в БД
    if argum == 'start':
        adding_user_id.adding_user_id(table_name=arg_role,
                                      user_id=message.from_user.id,
                                      user_name=message.from_user.username)
        adding_stat(user_id=message.from_user.id,
                    user_name=message.from_user.username,
                    name=message.from_user.first_name,
                    last_name=message.from_user.last_name)

    try:
        mes_to_rep = message.reply_to_message.text
        if mes_to_rep == 'Передайте свою геопозицию в качестве начальной точки - ' \
                         'соответствующая кнопка\n' \
                         'или введите 🏙 город (ПГТ, село) начала маршрута.\n\n' \
                         '❗️ВНИМАНИЕ❗ (при вводе вручную)️\n\n ' \
                         'неправильные запросы:\n ' \
                         '❌Киев, Жилянская 24\n ' \
                         '❌Святопетровское Леси украинки 2\n\n ' \
                         'правильные запросы:\n ' \
                         '✅Киев\n ' \
                         '✅Святопетровское':
            bot.send_chat_action(message.chat.id, 'find_location')
            bot.delete_message(message.chat.id, message_id_to_del)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('/start', '/help')

            bot.send_message(message.chat.id,
                             'отлично, мы приняли это местоположение в качестве Вашей начальной точки!',
                             reply_markup=markup)
            working_with_db.manage_db(user_id=message.from_user.id,
                                      column_to_change='start_lat',
                                      data_to_chanme=message.location.latitude,
                                      tab_name=arg_role)
            working_with_db.manage_db(user_id=message.from_user.id,
                                      column_to_change='start_lon',
                                      data_to_chanme=message.location.longitude,
                                      tab_name=arg_role)

            try:
                geolocator = Nominatim(user_agent="my-application")
                address_driver = geolocator.reverse(f"{str(message.location.latitude)},"
                                                    f" {str(message.location.longitude)}",
                                                    language=message.from_user.language_code).address

                address_driver = address_driver.split(',')
                street_driver = ', '.join(address_driver[4::-1])
                city_driver = address_driver[-3]

                working_with_db.manage_db(message.from_user.id,
                                          'start_street',
                                          street_driver,
                                          arg_role)

                working_with_db.manage_db(message.from_user.id,
                                          'start_city',
                                          city_driver,
                                          arg_role)

            except Exception as e:
                print(f'geolocation in chose_city{e}')
            apply_chosen_address.applying_chosen_address(message, argum, arg_role)

    except Exception:
        if message.text == None or message.text == 'None':
            bot.register_next_step_handler(message,
                                           chose_city,
                                           'start',
                                           message_id_to_del,
                                           'driver',
                                           bot)
        elif (str(message.text)).lower() == '/start':
            main.start(message)

        elif (str(message.text)).lower() == '/help':
            main.help(message)

        else:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.delete_message(message.chat.id, message_id_to_del)
            except Exception:
                pass
            try:

                geolocator = Nominatim(user_agent="my-application")

                location = geolocator.geocode(f"{message.text}, Украина",
                                              language=message.from_user.language_code)




            except Exception as e:
                print(f"geolocation in choose_city {e}")
            try:
                if location != None:

                    # ???neponiatno
                    bot.clear_reply_handlers_by_message_id(message.chat.id)

                    # переходим в работу с базой даных водителя
                    working_with_db.manage_db(message.from_user.id,
                                              f'{argum}_city',
                                              message.text,
                                              arg_role)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row('/start', '/help')
                    if argum == 'start':

                        message_id_to_del = bot.send_message(message.chat.id,
                                                             "Введите 🏡 улицу и номер дома начальной точки:\n"
                                                             "(например Победы 24 или метро университет)",
                                                             reply_markup=markup).message_id
                    if argum == 'end':
                        message_id_to_del = bot.send_message(message.chat.id,
                                                             "Введите 🏡 улицу и номер дома финальной точки:\n"
                                                             "(например Победы 24 или метро университет)",
                                                             reply_markup=markup).message_id
                    # переходит на следующий шаг - ф-я "chose_start_route"
                    bot.register_next_step_handler(message,
                                                   chosing_street.chose_route,
                                                   argum,
                                                   message_id_to_del,
                                                   arg_role,
                                                   bot)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.row('/start', '/help')
                    message_id_to_del = bot.send_message(message.from_user.id,
                                                         "Вы ввели неправильный 🏙 "
                                                         "город попробуйте по другому!",
                                                         reply_markup=markup).message_id
                    bot.register_next_step_handler(message,
                                                   chose_city,
                                                   argum,
                                                   message_id_to_del,
                                                   arg_role,
                                                   bot)
            except Exception:
                pass
