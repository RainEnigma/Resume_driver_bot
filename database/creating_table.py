from contextlib import closing
import data.datas

import psycopg2


def creating_table(table_name, connection, data):
    with connection.cursor() as cursor:
        '''This will delete table:'''

        # cursor.execute(f"""drop table if exists {table_name} cascade""")

        '''creating table'''

        text_columns = ''
        for key, value in data.items():
            text_columns += (f"{key} {value},")
        cursor.execute(f"""create table if not exists {table_name} ({text_columns.rstrip(',')})""")


def creating_tables_in_DB(table_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:
        conn.autocommit = True

        '''creating table'''

        creating_table(table_name=table_name,
                       connection=conn,
                       data={
                           'user_id': 'integer',
                           'm_date': 'varchar',
                           'm_time': 'varchar',
                           'start_city': 'varchar',
                           'start_street': 'varchar',
                           # 'start_building': 'varchar',
                           'end_city': 'varchar',
                           'end_street': 'varchar',
                           # 'end_building': 'varchar',
                           'start_lat': 'float',
                           'start_lon': 'float',
                           'end_lat': 'float',
                           'end_lon': 'float',
                           'date_time': 'varchar',
                           'time_format': 'integer',
                           'user_name': 'varchar'

                       })
