import os
import psycopg2

try:
    from local_settings import DATABASE_URL_ELEPHANT_SQL
except ImportError:
    DATABASE_URL_ELEPHANT_SQL = os.environ.get("DATABASE_URL_ELEPHANT_SQL")


conn = psycopg2.connect(DATABASE_URL_ELEPHANT_SQL, sslmode='require')


def reconnect():
    global conn
    return psycopg2.connect(DATABASE_URL_ELEPHANT_SQL, sslmode='require')
