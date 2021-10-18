import apply_chosen_address
from database import selecting_data, working_with_db
from geopy.geocoders import Nominatim
import main
from telebot import types


def chose_route(message, argum, message_to_del, arg_role, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/start', '/help')
    try:
        bot.delete_message(message.chat.id, message_to_del)
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass
    if (str(message.text)).lower() == '/start':
        main.start(message)
    elif (str(message.text)).lower() == '/help':
        main.help(message)


    else:
        answers_cur = selecting_data.select_data(user_id=message.from_user.id,
                                                 row_name=f'{argum}_city',
                                                 tab_name=f'{arg_role}')

        try:
            geolocator = Nominatim(user_agent="my-application")
            # подумать про кортеж

            location = geolocator.geocode({"country": "Украина",
                                           "city": {answers_cur[0][0]},
                                           "street": message.text},
                                          # location = geolocator.geocode(f"{message_text}, {answers_cur[0][0]}, Украина",
                                          language=message.from_user.language_code)
            bot.send_location(message.chat.id,
                              latitude=location.latitude,
                              longitude=location.longitude)
            bot.send_message(message.chat.id,
                             location.address)

            # добавляем в базу даных ячейки lon,lat начальной точки
            working_with_db.manage_db(message.from_user.id,
                                      f'{argum}_lon',
                                      location.longitude,
                                      arg_role)

            working_with_db.manage_db(message.from_user.id,
                                      f'{argum}_lat',
                                      location.latitude,
                                      arg_role)

            working_with_db.manage_db(message.from_user.id,
                                      f'{argum}_street',
                                      message.text, arg_role)

            bot.clear_reply_handlers_by_message_id(message.chat.id)

            apply_chosen_address.applying_chosen_address(message, argum, arg_role)


        except Exception as e:
            print(f"problem in chose_route_func {e}")

            message_to_del = bot.send_message(message.from_user.id,
                                              "Вы ввели несуществующий адрес, "
                                              "попробуйте по другому!\n"
                                              "например: Победы 24 или метро Университет",
                                              reply_markup=markup).message_id
            bot.register_next_step_handler(message,
                                           chose_route,
                                           argum,
                                           message_to_del,
                                           arg_role,
                                           bot)
