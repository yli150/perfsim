from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from .statistics import Statistics


@dataclass
class Context:
    env: simpy.Environment = field(default=simpy.Environment())
    barrierMgr: BarrierMgr = field(default=BarrierMgr())
    statistic: Statistics = field(default=Statistics())
