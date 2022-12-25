import os
import psycopg2

try:
    from local_settings import DATABASE_URL_ELEPHANT_SQL
except ImportError:
    DATABASE_URL_ELEPHANT_SQL = os.environ.get("DATABASE_URL_ELEPHANT_SQL")


def connect():
    return psycopg2.connect(DATABASE_URL_ELEPHANT_SQL, sslmode='require')


class Connection:
    def __init__(self):
        self.conn = connect()

    def get_connection(self):
        if self.closed:
            self.reconnect()

    @property
    def closed(self):
        return self.conn.closed

    def close(self):
        self.conn.close()

    def reconnect(self):
        self.conn = connect()

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()


connection = Connection()
