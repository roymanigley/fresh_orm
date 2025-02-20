# fresh_orm
![Unit-Tests](https://github.com/roymanigley/fresh_orm/actions/workflows/test.yml/badge.svg)  
![Published Python Package](https://github.com/roymanigley/fresh_orm/actions/workflows/publish.yml/badge.svg)

# Fresh ORM

A lightweight SQLite Object-Relational Mapping (ORM) library for Python, designed to simplify database interactions and provide an intuitive interface for managing SQLite tables and relationships.

## Features

1. **Foreign Key Support**
   - Foreign keys are mapped to integers (`INTEGER` type in SQLite), enabling relationships between tables.

2. **Table Creation**
   - Automatically generates SQLite tables based on Python model definitions.

3. **CRUD Operations**
   - **`create`:** Insert new records into a table.
   - **`update`:** Update specific fields of existing records.
   - **`by_id`:** Retrieve a single record by its primary key.
   - **`all`:** Fetch all records from a table.
   - **`filter`:** Query records based on specific conditions with support for logical operations.

4. **Seamless Mapping**
   - Define models as Python classes and map them directly to SQLite tables without boilerplate code.

## Example Usage

```python
from dataclasses import dataclass

from fresh_orm.config import DbConfig
from fresh_orm.model import BaseModel
from fresh_orm.repository import BaseRepository


@dataclass
class DummyType(BaseModel):
   name: str = None

@dataclass
class Dummy(BaseModel):
   name: str = None
   type: DummyType = None

class DummyTypeRepo(BaseRepository[DummyType]):
   model = DummyType

class DummyRepo(BaseRepository[Dummy]):
   model = Dummy

DbConfig.init_tables([Dummy, DummyType])

dummy_type = DummyTypeRepo.create(DummyType(name='Test Dummy Type'))
dummy: Dummy = DummyRepo.create(Dummy(name='Test Dummy', type=dummy_type))

dummy_from_db: Dummy = DummyRepo.by_id(dummy.id)

assert dummy_from_db.name == dummy.name
assert dummy_from_db.type == dummy.type.id
```