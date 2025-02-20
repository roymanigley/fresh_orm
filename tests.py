import unittest
from dataclasses import dataclass

from fresh_orm.config import DbConfig
from fresh_orm.model import BaseModel
from fresh_orm.repository import BaseRepository


class BasicTest(unittest.TestCase):

    def setUp(self):
        DbConfig.db_file = ':memory:'
        DbConfig.reset_connection()

    def test_create_get_by_id(self):
        @dataclass
        class Dummy(BaseModel):
            name: str = None

        class DummyRepo(BaseRepository[Dummy]):
            model = Dummy

        DbConfig.init_tables([Dummy])

        dummy: Dummy = DummyRepo.create(Dummy(name='Test Dummy'))
        dummy_from_db: Dummy = DummyRepo.by_id(dummy.id)
        self.assertIsNotNone(dummy_from_db.id)
        self.assertEqual(dummy, dummy_from_db)

    def test_update_get_by_id(self):
        @dataclass
        class Dummy(BaseModel):
            name: str = None

        class DummyRepo(BaseRepository[Dummy]):
            model = Dummy

        DbConfig.init_tables([Dummy])

        dummy: Dummy = DummyRepo.create(Dummy(name='Test Dummy'))
        updated_dummy: Dummy = Dummy(name='aaaa', id=dummy.id)
        DummyRepo.update(updated_dummy)
        dummy_from_db: list[Dummy] = DummyRepo.by_id(dummy.id)
        self.assertNotEqual(dummy, dummy_from_db)
        self.assertEqual(updated_dummy, dummy_from_db)

    def test_find_all(self):
        @dataclass
        class Dummy(BaseModel):
            name: str = None

        class DummyRepo(BaseRepository[Dummy]):
            model = Dummy

        DbConfig.init_tables([Dummy])
        for i in range(10):
            DummyRepo.create(Dummy(name=f'Test Dummy {i}'))
        dummies_from_db: list[Dummy] = DummyRepo.all()
        self.assertEqual(10, len(dummies_from_db))

    def test_filter(self):
        @dataclass
        class Dummy(BaseModel):
            name: str = None

        class DummyRepo(BaseRepository[Dummy]):
            model = Dummy

        DbConfig.init_tables([Dummy])
        for i in range(1, 11):
            DummyRepo.create(Dummy(name=f'Test Dummy {i}'))
        dummies_from_db: list[Dummy] = DummyRepo.filter(name='Test Dummy 2')
        self.assertEqual(1, len(dummies_from_db))
        self.assertEqual(2, dummies_from_db[0].id)
        self.assertEqual('Test Dummy 2', dummies_from_db[0].name)

    def test_delete(self):
        @dataclass
        class Dummy(BaseModel):
            name: str = None

        class DummyRepo(BaseRepository[Dummy]):
            model = Dummy

        DbConfig.init_tables([Dummy])

        dummy: Dummy = DummyRepo.create(Dummy(name='Test Dummy'))
        DummyRepo.delete(dummy.id)
        dummy_from_db = DummyRepo.by_id(dummy.id)
        self.assertIsNone(dummy_from_db)


class ForeignKeyTest(unittest.TestCase):

    def setUp(self):
        DbConfig.db_file = ':memory:'
        DbConfig.reset_connection()

    def test_create(self):
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
        self.assertEqual(dummy_from_db.name, dummy.name)
        self.assertEqual(dummy_from_db.type, dummy.type.id)


if __name__ == '__main__':
    unittest.main()
