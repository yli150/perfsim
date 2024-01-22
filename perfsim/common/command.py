from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


@dataclass
class RequestCmd:
    name: str
    type: str
    id: int
    pdeps: List[int] = field(default_factory=list)
    cdeps: List[int] = field(default_factory=list)

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