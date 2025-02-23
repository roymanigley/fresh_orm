from abc import ABC
from dataclasses import dataclass


@dataclass
class BaseModel(ABC):

    id: int = None

    class Meta:
        table_name = None
