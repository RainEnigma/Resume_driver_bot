from database import working_with_db, selecting_data
import datetime
from datetime import timedelta
import psycopg2
from contextlib import closing
from data import datas
from telebot import types


def chose_time(message, f_data, message_id_to_del, arg_role, bot):
    markup_start_help = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup_start_help.row('/start', '/help')
    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message_id_to_del)
    except Exception:
        pass
    working_with_db.manage_db(message.from_user.id, 'm_date', f_data, arg_role)
    time_format = message.text.split(":")

    try:
        try_time_format = datetime.datetime.strptime(message.text, '%H:%M')

        working_with_db.manage_db(message.from_user.id, 'm_time', message.text, arg_role)
        working_with_db.manage_db(message.from_user.id, 'time_format',
                                  int(f'{time_format[0]}{time_format[1]}'),
                                  arg_role)
        answers_cur = selecting_data.select_data(user_id=message.from_user.id,
                                                 row_name='*',
                                                 tab_name=arg_role)

        if arg_role == 'passenger':

            pass_strt_lat = answers_cur[0][7]
            pass_strt_lon = answers_cur[0][8]
            pass_end_lat = answers_cur[0][9]
            pass_end_lon = answers_cur[0][10]
            pass_date = answers_cur[0][1]
            lag = 45
            passenger_time = f'{answers_cur[0][1]} {answers_cur[0][2]}'
            passenger_time_formated = datetime.datetime.strptime(passenger_time, '%d.%m.%Y %H:%M')
            time_from = str(passenger_time_formated + timedelta(minutes=-lag))[-8:-3]
            time_from = int(f'{time_from[0:2]}{time_from[3:]}')
            time_to = str(passenger_time_formated + timedelta(minutes=lag))[-8:-3]
            time_to = int(f'{time_to[0:2]}{time_to[3:]}')
            # мегавыборка)))
            with closing(psycopg2.connect(dbname=datas.name_DB,
                                          user=datas.user_DB,
                                          password=datas.password_DB,
                                          host=datas.host_DB)) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""SELECT user_id, m_date, m_time, start_city,start_street,end_city,end_street,user_name
                        FROM driver
                        WHERE {pass_strt_lat - 0.015} <= start_lat 
                        and {pass_strt_lat + 0.015} >= start_lat
                        and {pass_strt_lon - 0.015} <= start_lon
                        and {pass_strt_lon + 0.015} >= start_lon
                        and {pass_end_lat - 0.015} <= end_lat
                        and {pass_end_lat + 0.015} >= end_lat
                        and {pass_end_lon - 0.015} <= end_lon
                        and {pass_end_lon + 0.015} >= end_lon
                        and '{pass_date}' = m_date
                        and '{time_from}' <= time_format
                        and '{time_to}' >= time_format
                    """)

                    answers_curs = cursor.fetchall()
                if answers_cur[0][13] == "None":
                    user_name = "[username отсутствует]"
                else:
                    user_name = f"@{answers_cur[0][13]}"
                bot.send_message(-1001476270227,
                                 f"🚶‍ Новая поездка от {user_name}:\n"
                                 f"⏰{answers_cur[0][2]}  📆{answers_cur[0][1]}\n"
                                 f"⏩ {answers_cur[0][3]}, {answers_cur[0][4]}\n"
                                 f"⛔ {answers_cur[0][5]}, {answers_cur[0][6]}")

                bot.send_message(message.chat.id,
                                 f"🚶‍ Поздравляем! Ваша поездка создана:\n"
                                 f"⏰{answers_cur[0][2]}  📆{answers_cur[0][1]}\n"
                                 f"⏩ {answers_cur[0][3]}, {answers_cur[0][4]}\n"
                                 f"⛔ {answers_cur[0][5]}, {answers_cur[0][6]}",
                                 reply_markup=markup_start_help)

                if len(answers_curs) != 0:
                    for driver in answers_curs:

                        try:
                            img = bot.get_user_profile_photos(user_id=driver[0], limit=1)
                            bot.send_photo(message.chat.id,
                                           img.photos[0][0].file_id,
                                           parse_mode="html",
                                           caption=f"!ВНИМАНИЕ!\n"
                                                   f"🚙 Водитель @{driver[7]}:\n"
                                                   f"⏰{driver[2]}  📆{driver[1]}\n"
                                                   f"⏩ {driver[3]}, {driver[4]}\n"
                                                   f"⛔ {driver[5]}, {driver[6]}")
                        except Exception:
                            bot.send_message(message.chat.id, f"Фото профиля отсутствует!\n"
                                                              f"🚙 Водитель @{driver[7]}:\n"
                                                              f"⏰{driver[2]}  📆{driver[1]}\n"
                                                              f"⏩ {driver[3]}, {driver[4]}\n"
                                                              f"⛔ {driver[5]}, {driver[6]}")

                        list_drivers = selecting_data.select_data(message.from_user.id,
                                                                  'date_time',
                                                                  'passenger')[0][0]
                        if list_drivers == None:
                            working_with_db.manage_db(message.from_user.id, 'date_time',
                                                      f'{driver[0]}', arg_role)
                        else:
                            working_with_db.manage_db(message.from_user.id, 'date_time',
                                                      f'{list_drivers},{driver[0]}', arg_role)

                else:
                    bot.send_message(message.chat.id,
                                     "Извините, в даный момент нет водтелей по Вашему маршруту.\n"
                                     "Мы уведомим Вас как только кто-нибудь появится!!!")


        elif arg_role == 'driver':

            working_with_db.manage_db(message.from_user.id, 'date_time',
                                      f'{answers_cur[0][1]} {answers_cur[0][2]}', 'driver')
            try:
                bot.send_message(-1001476270227,
                                 f"🚙 Новая поездка от @{answers_cur[0][13]}:\n"
                                 f"⏰{answers_cur[0][2]}  📆{answers_cur[0][1]}\n"
                                 f"⏩ {answers_cur[0][3]}, {answers_cur[0][4]}\n"
                                 f"⛔ {answers_cur[0][5]}, {answers_cur[0][6]}\n")
            except Exception:
                pass

            bot.send_message(message.from_user.id,
                             f"🚙 Поздравляем! Ваша поездка создана:\n"
                             f"⏰{answers_cur[0][2]}  📆{answers_cur[0][1]}\n"
                             f"⏩ {answers_cur[0][3]}, {answers_cur[0][4]}\n"
                             f"⛔ {answers_cur[0][5]}, {answers_cur[0][6]}\n"
                             f"Ваши пассажиры скоро свяжутся с Вами",
                             reply_markup=markup_start_help)

            passenger_time = f'{answers_cur[0][1]} {answers_cur[0][2]}'
            passenger_time_formated = datetime.datetime.strptime(passenger_time, '%d.%m.%Y %H:%M')


    except Exception:
        message_id_to_del = bot.send_message(message.chat.id,
                                             "Вы ввели неверный формат времени, попробуйте еще раз (формат 00:00):").message_id
        bot.register_next_step_handler(message,
                                       chose_time,
                                       f_data, message_id_to_del, arg_role, bot)
