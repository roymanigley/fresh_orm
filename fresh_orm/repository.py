import datetime
import json
from typing import TypeVar, Generic, List, Dict, Any

from fresh_orm import model
from fresh_orm.config import DbConfig, ModelField
from fresh_orm.model import BaseModel

T = TypeVar("T", bound="BaseModel")


class BaseRepository(Generic[T]):
    model: 'model.BaseModel' = None

    @classmethod
    def all(cls) -> List[T]:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        query = f"SELECT * FROM {table}"
        cursor = conn.execute(query)
        results = cursor.fetchall()
        rows = [cls.model(**dict(zip([col[0] for col in cursor.description], row))) for row in results]
        return [cls._map_row_to_python(r) for r in rows]

    @classmethod
    def filter(cls, **kwargs) -> List[T]:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        query = f"SELECT * FROM {table} t WHERE"
        for key in kwargs.keys():
            query += f' t.{key} = ?'
        cursor = conn.execute(query, list(kwargs.values()))
        results = cursor.fetchall()
        rows = [cls.model(**dict(zip([col[0] for col in cursor.description], row))) for row in results]
        return [cls._map_row_to_python(r) for r in rows]

    @classmethod
    def by_id(cls, id: int) -> T:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        query = f"SELECT * FROM {table} t WHERE t.id = ?"
        cursor = conn.execute(query, [id])
        result = cursor.fetchone()
        if result:
            row = cls.model(**dict(zip([col[0] for col in cursor.description], result)))
            return cls._map_row_to_python(row)
        return None

    @classmethod
    def create(cls, record: T) -> T:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        fields = record.__dict__.keys()
        values = [(v.id if issubclass(v.__class__, BaseModel) else v) for v in record.__dict__.values()]
        values = [(json.dumps(v) if isinstance(v, dict) or isinstance(v, dict) else v) for v in values]
        placeholders = ", ".join("?" for _ in fields)
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        c = conn.execute(query, values)
        conn.commit()
        record.id = c.lastrowid
        return record

    @classmethod
    def update(cls, record: T) -> T:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        fields = record.__dict__.keys()
        values = [(v.id if issubclass(v.__class__, BaseModel) else v) for v in record.__dict__.values()]
        values = [(json.dumps(v) if isinstance(v, dict) or isinstance(v, dict) else v) for v in values]
        placeholders = ", ".join(f"{field} = ?" for field in fields)
        query = f"UPDATE {table} SET {placeholders} WHERE ID=?"
        c = conn.execute(query, list(values) + [record.id])
        conn.commit()
        record.id = c.lastrowid
        return record

    @classmethod
    def delete(cls, id: int) -> None:
        conn = DbConfig.get_connection()
        table = DbConfig.get_table_name(cls.model)
        conn.execute(
            f'DELETE FROM {table} as t WHERE t.id = ?',
            [id]
        )
        conn.commit()

    @classmethod
    def _map_row_to_python(cls, row: T) -> T:
        for field in ModelField.from_model_class(cls.model):
            value = getattr(row, field.name)
            if value is None:
                setattr(row, field.name, None)
                continue

            # Convert SQLite types back to Python types
            if field.type == int:
                setattr(row, field.name, int(value))
            elif field.type == float:
                setattr(row, field.name, float(value))
            elif field.type == bool:
                setattr(row, field.name, bool(value))
            elif field.type in (dict, list):  # JSON field
                setattr(row, field.name, json.loads(value))
            elif field.type == datetime.date:
                setattr(row, field.name, datetime.date.fromisoformat(value))
            elif field.type == datetime.datetime:
                setattr(row, field.name, datetime.datetime.fromisoformat(value))

        return row