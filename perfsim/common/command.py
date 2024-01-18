from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class RequestCmd:
    name: str
    type: str
    id: int

    def __str__(self) -> str:
        return f'{self.name}_{self.id}_{self.type}'


class MemOp(Enum):
    READ = auto()
    WRITE = auto()


@dataclass
class MemCmd:
    name: str
    type: MemOp
    id: int
    size: int

    def __str__(self) -> str:
        return f'{self.name}_{self.id}_{self.type.name}_{self.size}'