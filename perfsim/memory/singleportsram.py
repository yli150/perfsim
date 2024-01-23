from .memoryabc import Memory
from ..engine.enginebase import EngineBase
from perfsim.common.command import MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
import simpy
from typing import List
from ..context.context import Context


class SinglePortSRAM(Memory):
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)

    def post_init(self):
        super().post_init()
        self.readQ = simpy.Store(self.env, capacity=10)
        self.writeQ = simpy.Store(self.env, capacity=10)
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event
        while True:
            cmd = yield self.cmd_in_queue.get()
            if cmd.type == MemOp.READ:
                latency = max(cmd.size, 1)
                print(f'Device {self.name} READ {cmd},  takes {latency} to process at {self.env.now}')
            else:
                latency = cmd.size * 2
                print(f'Device {self.name} WRITE {cmd},  takes {latency} to process at {self.env.now}')

            yield self.env.timeout(latency)
            yield self.cmd_out_queue.put(cmd)

    def request(self, memCmd):
        yield self.cmd_in_queue.put(memCmd)
