import os
import psycopg2

try:
    from local_settings import DATABASE_URL
except ImportError:
    DATABASE_URL = os.environ.get("DATABASE_URL")


conn = psycopg2.connect(DATABASE_URL, sslmode='require')


def reconnect():
    global conn
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
