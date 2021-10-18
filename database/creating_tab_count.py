from contextlib import closing
import data.datas

import psycopg2


def create_tab_count(table_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                f"""create table if not exists {table_name} (
                           numb SERIAL PRIMARY KEY,
                           user_id integer,
                           name varchar,
                           user_name varchar,
                           last_name varchar,
                           date_add varchar,
                           smthels varchar
                )""")
