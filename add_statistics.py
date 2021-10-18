from contextlib import closing
import datetime

import psycopg2
import data.datas


def adding_stat(user_id, user_name, name, last_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:

        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT user_id
                               FROM users
                               WHERE '{user_id}' = user_id 
                            """)
            answers_cur = cursor.fetchall()

            if len(answers_cur) == 0:

                cursor.execute(f"""insert into users (user_id, name, user_name, last_name, date_add)
                            values (
                                    '{user_id}',
                                    '{name}',
                                    '{user_name}',
                                    '{last_name}',
                                    '{str(datetime.datetime.now())}');""")

            else:
                pass
