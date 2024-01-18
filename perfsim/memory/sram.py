from .memoryabc import Memory
from ..engine.enginebase import EngineBase
from perfsim.common.command import MemCmd, MemOp
import simpy
from typing import List


class SRAM(Memory):
    def __init__(self, env, name: str) -> None:
        super().__init__(env, name)

    def post_init(self):
        super().post_init()
        self.readQ = simpy.Store(self.env, capacity=10)
        self.writeQ = simpy.Store(self.env, capacity=10)
        self.readprc = self.env.process(self.read())
        self.writeprc = self.env.process(self.write())

    def run(self, cmds: List):
        yield self.start_event
        for memCmd in cmds:
            if memCmd.type == MemOp.READ:
                yield self.readQ.put(memCmd)
            if memCmd.type == MemOp.WRITE:
                yield self.writeQ.put(memCmd)

    def read(self):
        while True:
            rdcmd = yield self.readQ.get()
            latency = max(rdcmd.size, 1)
            print(f'Device {self.name} READ {rdcmd},  takes {latency} to process at {self.env.now}')
            yield self.env.timeout(latency)
            yield self.cmd_out_queue.put(rdcmd)

    def write(self):
        while True:
            wrcmd = yield self.writeQ.get()
            latency = wrcmd.size * 2
            print(f'Device {self.name} WRITE {wrcmd},  takes {latency} to process at {self.env.now}')
            yield self.env.timeout(latency)
            yield self.cmd_out_queue.put(wrcmd)
