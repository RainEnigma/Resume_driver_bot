from contextlib import closing
import data.datas
import psycopg2


def adding_user_id(table_name, user_id, user_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:

        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(f"""SELECT user_id
                               FROM {table_name}
                               WHERE '{user_id}' = user_id 
                            """)
            answers_cur = cursor.fetchall()

            if len(answers_cur) == 0:

                cursor.execute(f"""insert into {table_name} (user_id, user_name)
                            values ('{user_id}', '{user_name}');""")

            else:
                pass
