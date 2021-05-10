from database import conn

TABLE = 'stat'


def add_value(name: str, number: int = 1) -> None:
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE} SET count=count+{number} WHERE name='{name}';")
    conn.commit()


def get_value(name: str) -> int:
    cur = conn.cursor()
    cur.execute(f"SELECT count FROM {TABLE} WHERE name='{name}';")
    return cur.fetchone()[0]
