import sqlite3
from typing import List

from fresh_orm.model import BaseModel


class DbConfig:
    db_file = '../db.sqlite'
    _conn: sqlite3.Connection = None

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        if not cls._conn:
            cls._conn = sqlite3.connect(cls.db_file)
        return cls._conn

    @classmethod
    def init_tables(cls, models: List[BaseModel]) -> None:
        conn = cls.get_connection()
        for model in models:
            field_definitions = ', '.join(model.get_field_definitions())
            query = f"CREATE TABLE IF NOT EXISTS {model.get_table_name()} ({field_definitions})"
            print(query)
            conn.execute(query)

    @classmethod
    def reset_connection(cls) -> None:
        cls._conn = None
