import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

con = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    host='35.239.215.17',
    port = '27017',
    password='postgres')
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()
cur.execute('CREATE DATABASE new_database')
