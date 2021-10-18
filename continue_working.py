import psycopg2, telebot
from contextlib import closing
from data import datas
from check_new_driver import check_new_driver_start
import datetime
from database import delete_data
from data import config

bot = telebot.TeleBot(config.API_TOKEN)


def continue_working():
    # a = datetime.datetime.now().time()
    # if a.hour == 12 and a.minute == 10:
    #     with closing(psycopg2.connect(dbname=datas.name_DB,
    #                                   user=datas.user_DB,
    #                                   password=datas.password_DB,
    #                                   host=datas.host_DB)) as conn:
    #         conn.autocommit = True
    #         with conn.cursor() as cursor:
    #             cursor.execute(f"""SELECT numb FROM users""")
    #             answers_cur = cursor.fetchall()
    #     bot.send_sticker(-1001476270227, "CAACAgIAAxkBAAIBJ16ioxmFcFv0hhRDl-2vU-RWHozvAAJaBwACRvusBIK0AX12IQG3GQQ")
    #     bot.send_message(-1001476270227,
    #                      f"🚙 🤖ПОДКИНЬ МЕНЯ:\n"
    #                      f"Сегодня нас уже {answers_cur[-1][0]}\n"
    #                      f"Спасибо вам за активность в создании поездок! Чем больше мы создаем "
    #                      f"поездок - тем больше направлений у нас есть!")

    with closing(psycopg2.connect(dbname=datas.name_DB,
                                  user=datas.user_DB,
                                  password=datas.password_DB,
                                  host=datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT *
                                FROM passenger
                                where m_date IS NOT NULL
                                and m_time IS NOT NULL
                                and start_lat IS NOT NULL
                                and start_lon IS NOT NULL
                                and end_lat IS NOT NULL
                                and end_lon IS NOT NULL
                            """)
            passengers_accepted_conditions = cursor.fetchall()
            try:
                for passenger in passengers_accepted_conditions:
                    passenger_time = f'{passenger[1]} {passenger[2]}'
                    passenger_time_formated = datetime.datetime.strptime(passenger_time,
                                                                         '%d.%m.%Y %H:%M')
                    if passenger_time_formated <= datetime.datetime.now():
                        delete_data.delete_data(passenger[0],
                                                'user_id',
                                                'passenger')
                        bot.send_message(passenger[0],
                                         "Поездка удалена, так как ее время пришло🦠\n"
                                         "чтоб начать создание поездки нажмите \n"
                                         "/start))")
                    else:
                        check_new_driver_start(bot, passenger)

            except Exception:
                pass

        # Проверяем драйвера на удаление

        date_to_check = datetime.datetime.now().strftime("%d.%m.%Y")
        time_to_check = datetime.datetime.now().strftime("%H%M")
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT user_id
                                    FROM driver
                                    where '{date_to_check}' = m_date 
                                    and '{time_to_check}' >= time_format
                                    
                                """)
            drivers_time_over = cursor.fetchall()
            try:
                for driver_id in drivers_time_over:
                    delete_data.delete_data(driver_id[0], 'user_id', 'driver')

                    bot.send_message(driver_id[0], "Поездка 🚙 удалена, так как ее время пришло🦠\n"
                                                   "чтоб начать создание поездки нажмите \n"
                                                   "/start")
            except Exception:
                pass
