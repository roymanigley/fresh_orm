from dataclasses import dataclass
from typing import Optional

from fresh_orm import model
from fresh_orm.config import DbConfig
from fresh_orm.repository import BaseRepository


@dataclass()
class Type(model.BaseModel):
    name: Optional[str] = None


@dataclass()
class Dummy(model.BaseModel):
    name: Optional[str] = None
    type: Optional[Type] = None

    def test(self):
        print('test')


class DummyRepo(BaseRepository[Dummy]):
    model = Dummy

class TypeRepo(BaseRepository[Type]):
    model = Type


DbConfig.init_tables([Dummy, Type])

type = TypeRepo.create(Type(name='aaa'))
DummyRepo.create(Dummy(name='aaa', type=type))

# r: Dummy = DummyRepo.all()[0]
#
# r.name = 'ioioioi'
#
# DummyRepo.update(r)

print(DummyRepo.all())
print(DummyRepo.filter(type=4))
