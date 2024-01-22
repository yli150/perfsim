from .barrier import Barrier
import collections


class BarrierMgr():
    def __init__(self) -> None:
        self.barrierdict = {}

    def add(self, barrier: Barrier):
        self.barrierdict[barrier.id] = barrier

    def get(self, id: int):
        return self.barrierdict[id]