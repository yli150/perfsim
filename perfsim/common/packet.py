from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List
from .command import RequestCmd
from .devicedes import DeviceDesc


@dataclass
class StatisticPacket:
    cmd: RequestCmd
    devicedes: DeviceDesc
    startT: int = field(default=0)
    endT: int = field(default=0)

    def start(self, t: int):
        self.startT = t

    def terminate(self, t: int):
        self.endT = t

    # proxy to command class
    def __getattr__(self, name):
        if hasattr(self.cmd, name):
            return getattr(self.cmd, name)