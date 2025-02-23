import datetime
import inspect
import sqlite3
from dataclasses import dataclass
from typing import List, get_origin, Union, get_args, Type

from fresh_orm.model import BaseModel


@dataclass
class ModelField:
    name: str
    type: type
    is_optional: bool
    is_foreign_key: bool

    @classmethod
    def from_model_class(cls, model_class) -> List['ModelField']:
        fields = []
        for name, clazz in inspect.get_annotations(model_class).items():
            is_optional = get_origin(clazz) is Union
            is_fk =False
            if is_optional:
                clazz = get_args(clazz)[0]
            if issubclass(clazz, BaseModel):
                is_fk = True
            fields.append(
                ModelField(
                    name=name,
                    type=clazz,
                    is_optional=is_optional,
                    is_foreign_key=is_fk
                )
            )
        return fields

class DbConfig:
    db_file = 'db.sqlite'
    _conn: sqlite3.Connection = None

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        if not cls._conn:
            cls._conn = sqlite3.connect(cls.db_file)
        return cls._conn

    @classmethod
    def init_tables(cls, models: List[Type[BaseModel]]) -> None:
        conn = cls.get_connection()
        for model in models:
            field_definitions = ', '.join(DbConfig.get_field_definitions(model))
            query = f"CREATE TABLE IF NOT EXISTS {DbConfig.get_table_name(model)} ({field_definitions})"
            conn.execute(query)

    @classmethod
    def reset_connection(cls) -> None:
        cls._conn = None

    @classmethod
    def get_field_definitions(cls, model_class) -> List[str]:
        field_definitions = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
        fk_definitions = []
        for field in ModelField.from_model_class(model_class):
            if issubclass(field.type, BaseModel):
                fk_definitions.append(
                    f'FOREIGN KEY ({field.name}) REFERENCES {DbConfig.get_table_name(field.type)}(id)'
                )
            if field.type == int or field.is_foreign_key:
                db_type = 'INTEGER'
            elif field.type == float:
                db_type = 'REAL'
            elif field.type == bool:
                db_type = 'INTEGER'  # SQLite does not have a BOOLEAN type
            elif field.type == str:
                db_type = 'TEXT'
            elif field.type == dict or field.type == list:  # JSON field
                db_type = f'TEXT CHECK(json_valid({field.name}))'
            elif field.type == datetime.date:
                db_type = f'TEXT CHECK({field.name} LIKE "____-__-__")'  # YYYY-MM-DD
            elif field.type == datetime.datetime:
                db_type = f'TEXT CHECK({field.name} LIKE "____-__-__ __:__:__%")'  # YYYY-MM-DD HH:MM:SS
            else:
                db_type = 'TEXT'  # Default fallback
            field_definitions.append(f"{field.name} {db_type} {'NULL' if field.is_optional else 'NOT NULL'}")
        return field_definitions + fk_definitions

    @classmethod
    def get_table_name(cls, model_class) -> str:
        return model_class.Meta.table_name if model_class.Meta.table_name else model_class.__name__.lower()
