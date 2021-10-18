from contextlib import closing
import data.datas
import psycopg2


def manage_db(user_id, column_to_change, data_to_chanme, tab_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(f""" update {tab_name}
                                set {column_to_change} = '{data_to_chanme}' 
                                WHERE user_id = '{user_id}'""")
