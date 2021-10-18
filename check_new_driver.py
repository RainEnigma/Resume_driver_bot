import psycopg2, datetime
from contextlib import closing
from data import datas
from database import working_with_db
from datetime import timedelta
import logging.config

logging.config.fileConfig(fname='data/logging.conf')  # потом удалить?
logger = logging.getLogger(name="checkNewDriver")  # потом удалить?


def check_new_driver_start(bot, passenger):

    pass_start_lat = passenger[7]
    pass_start_lon = passenger[8]
    pass_end_lat = passenger[9]
    pass_end_lon = passenger[10]
    pass_date = passenger[1]
    lag = 45
    passenger_time = f'{passenger[1]} {passenger[2]}'
    passenger_time_formatted = datetime.datetime.strptime(passenger_time, '%d.%m.%Y %H:%M')
    time_from = str(passenger_time_formatted + timedelta(minutes=-lag))[-8:-3]
    time_from = int(f'{time_from[0:2]}{time_from[3:]}')
    time_to = str(passenger_time_formatted + timedelta(minutes=lag))[-8:-3]
    time_to = int(f'{time_to[0:2]}{time_to[3:]}')
    with closing(psycopg2.connect(dbname=datas.name_DB,
                                  user=datas.user_DB,
                                  password=datas.password_DB,
                                  host=datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                f"""SELECT user_id, m_date, m_time, start_city,start_street,end_city,end_street,user_name
                    FROM driver
                    WHERE {pass_start_lat - 0.015} <= start_lat 
                    and {pass_start_lat + 0.015} >= start_lat
                    and {pass_start_lon - 0.015} <= start_lon
                    and {pass_start_lon + 0.015} >= start_lon
                    and {pass_end_lat - 0.015} <= end_lat
                    and {pass_end_lat + 0.015} >= end_lat
                    and {pass_end_lon - 0.015} <= end_lon
                    and {pass_end_lon + 0.015} >= end_lon
                    and '{pass_date}' = m_date
                    and '{time_from}'<= time_format
                    and '{time_to}'>=time_format
                """)

            drivers_accepted_cond = cursor.fetchall()
        try:
            for driver in drivers_accepted_cond:
                if passenger[11] is None or str(driver[0]) not in passenger[11].split(','):
                    try:
                        img = bot.get_user_profile_photos(user_id=driver[0], limit=1)
                        bot.send_photo(passenger[0],
                                       img.photos[0][0].file_id,
                                       parse_mode="html",
                                       caption=f"!ВНИМАНИЕ!\n"
                        f"🚙 Новый водитель @{driver[7]}:\n"
                        f"⏰{driver[2]}  📆{driver[1]}\n"
                        f"⏩ {driver[3]}, {driver[4]}\n"
                        f"⛔ {driver[5]}, {driver[6]}")
                    except Exception:
                        bot.send_message(passenger[0], f"Фото профиля отсутствует!\n"
                                                       f"!ВНИМАНИЕ!\n"
                                                   f"🚙 Новый водитель @{driver[7]}:\n"
                                                   f"⏰{driver[2]}  📆{driver[1]}\n"
                                                   f"⏩ {driver[3]}, {driver[4]}\n"
                                                   f"⛔ {driver[5]}, {driver[6]}")

                    if passenger[11] is None or passenger[11] == '':
                        working_with_db.manage_db(user_id=passenger[0],
                                                  column_to_change='date_time',
                                                  data_to_chanme=f'{driver[0]}',
                                                  tab_name='passenger')
                    else:
                        working_with_db.manage_db(passenger[0],
                                                  'date_time',
                                                  f'{passenger[11]},{driver[0]}',
                                                  'passenger')
        except Exception:
            pass
