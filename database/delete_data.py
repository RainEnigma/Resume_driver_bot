import psycopg2
import data
from contextlib import closing
import logging.config


logging.config.fileConfig(fname='data/logging.conf')  # потом удалить?
logger = logging.getLogger(name="checkNewDriver")  # потом удалить?



def delete_data(user_id, columt_to_change, tab_name):
    with closing(psycopg2.connect(dbname=data.datas.name_DB,
                                  user=data.datas.user_DB,
                                  password=data.datas.password_DB,
                                  host=data.datas.host_DB)) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                    DELETE 
                    FROM {tab_name}
                    WHERE {columt_to_change} = '{user_id}'
                    """)
            logger.info(f'in table PASSENGER DELETED {user_id} row')
