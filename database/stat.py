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


def select_all() -> int:
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE};")
    return cur.fetchall()


def insert_value(id: int, name: str, value: int) -> None:
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {TABLE} VALUES {id, name, value};")


def delete_value(name: str) -> None:
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABLE} WHERE name='{name}';")
