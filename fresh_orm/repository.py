from typing import TypeVar, Generic, List

from fresh_orm import model
from fresh_orm.config import DbConfig
from fresh_orm.model import BaseModel

T = TypeVar("T", bound="BaseModel")


class BaseRepository(Generic[T]):
    model: 'model.BaseModel' = None

    @classmethod
    def all(cls) -> List[T]:
        conn = DbConfig.get_connection()
        table = cls.model.get_table_name()
        query = f"SELECT * FROM {table}"
        cursor = conn.execute(query)
        results = cursor.fetchall()
        return [cls.model(**dict(zip([col[0] for col in cursor.description], row))) for row in results]

    @classmethod
    def filter(cls, **kwargs) -> List[T]:
        conn = DbConfig.get_connection()
        table = cls.model.get_table_name()
        query = f"SELECT * FROM {table} t WHERE"
        for key in kwargs.keys():
            query += f' t.{key} = ?'
        cursor = conn.execute(query, list(kwargs.values()))
        results = cursor.fetchall()
        return [cls.model(**dict(zip([col[0] for col in cursor.description], row))) for row in results]

    @classmethod
    def by_id(cls, id: int) -> T:
        conn = DbConfig.get_connection()
        table = cls.model.get_table_name()
        query = f"SELECT * FROM {table} t WHERE t.id = ?"
        cursor = conn.execute(query, [id])
        result = cursor.fetchone()
        if result:
            return cls.model(**dict(zip([col[0] for col in cursor.description], result)))
        return None

    @classmethod
    def create(cls, record: T) -> T:
        conn = DbConfig.get_connection()
        table = cls.model.get_table_name()
        fields = record.__dict__.keys()
        values = [(v.id if issubclass(v.__class__, BaseModel) else v) for v in record.__dict__.values()]
        placeholders = ", ".join("?" for _ in fields)
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        c = conn.execute(query, values)
        conn.commit()
        record.id = c.lastrowid
        return record

    @classmethod
    def update(cls, record: T) -> T:
        conn = DbConfig.get_connection()
        table = cls.model.get_table_name()
        fields = record.__dict__.keys()
        values = record.__dict__.values()
        placeholders = ", ".join(f"{field} = ?" for field in fields)
        query = f"UPDATE {table} SET {placeholders} WHERE ID=?"
        c = conn.execute(query, list(values) + [record.id])
        conn.commit()
        record.id = c.lastrowid
        return record

    @classmethod
    def delete(cls, id: int) -> None:
        conn = DbConfig.get_connection()
        c = conn.execute(
            f'DELETE FROM {cls.model.get_table_name()} as t WHERE t.id = ?',
            [id]
        )
        conn.commit()
        print(c.lastrowid)