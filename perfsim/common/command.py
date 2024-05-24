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
class MemCmd(RequestCmd):
    size: int = field(default=0)

    def __str__(self) -> str:
        return f'MemCmd {self.name}_{self.id}_{self.type.name}_{self.size}'


@dataclass
class ComputeCmd(RequestCmd):
    macs: int = field(default=0)

    def __str__(self) -> str:
        return f'ComputeCmd {self.name}_{self.id}_{self.type.name}_{self.macs}'


@dataclass
class XferCmd(MemCmd):
    src: int = field(default=0)
    dst: int = field(default=0)

    def __str__(self) -> str:
        return f'XferCmd {self.name}_{self.id}_from_{self.src}_to_{self.dst}'