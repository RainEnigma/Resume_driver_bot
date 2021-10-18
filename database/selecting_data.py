import psycopg2
from contextlib import closing
import data


def select_data(user_id, row_name, tab_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT  {row_name}
                FROM {tab_name}
                WHERE user_id = {user_id}
                """)
            answers_cur = cursor.fetchall()

    return answers_cur
