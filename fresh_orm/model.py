import inspect
from abc import ABC
from dataclasses import dataclass
from typing import get_origin, Union, get_args, List


@dataclass
class ModelField:
    name: str
    type: type
    is_optional: bool
    is_foreign_key: bool


@dataclass
class BaseModel(ABC):

    id: int = None

    @classmethod
    def get_fields(cls) -> List[ModelField]:
        fields = []
        for name, clazz in inspect.get_annotations(cls).items():
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

    @classmethod
    def get_field_definitions(cls) -> List[str]:
        field_definitions = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
        fk_definitions = []
        for field in cls.get_fields():
            print(field)
            if issubclass(field.type, BaseModel):
                fk_definitions.append(
                    f'FOREIGN KEY ({field.name}) REFERENCES {field.type.get_table_name()}(id)'
                )
            if field.type == int or field.is_foreign_key:
                db_type = 'INTEGER'
            else:
                db_type = 'TEXT'
            field_definitions.append(f"{field.name} {db_type} {'NULL' if field.is_optional else 'NOT NULL'}")
        return field_definitions + fk_definitions

    @classmethod
    def get_table_name(cls) -> str:
        return cls.Meta.table_name if cls.Meta.table_name else cls.__name__.lower()

    class Meta:
        table_name = None
