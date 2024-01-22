from .memoryabc import Memory
from ..engine.enginebase import EngineBase
from perfsim.common.command import MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
import simpy
from typing import List


class SRAM(Memory):
    def __init__(self, env, barrierMgr: BarrierMgr, name: str) -> None:
        super().__init__(env, barrierMgr, name)

    def post_init(self):
        super().post_init()
        self.readQ = simpy.Store(self.env, capacity=10)
        self.writeQ = simpy.Store(self.env, capacity=10)
        self.readprc = self.env.process(self.read())
        self.writeprc = self.env.process(self.write())
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event

    def request(self, memCmd):
        if memCmd.type == MemOp.READ:
            yield self.readQ.put(memCmd)
        if memCmd.type == MemOp.WRITE:
            yield self.writeQ.put(memCmd)

    def read(self):
        while True:
            rdcmd = yield self.readQ.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in rdcmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            latency = max(rdcmd.size, 1)
            print(f'Device {self.name} READ {rdcmd},  takes {latency} to process at {self.env.now}')
            yield self.env.timeout(latency)
            yield self.cmd_out_queue.put(rdcmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in rdcmd.pdeps]
            for e in barrier_to_release:
                e.succeed()

    def write(self):
        while True:
            wrcmd = yield self.writeQ.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in wrcmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            latency = wrcmd.size * 2
            print(f'Device {self.name} WRITE {wrcmd},  takes {latency} to process at {self.env.now}')
            yield self.env.timeout(latency)
            yield self.cmd_out_queue.put(wrcmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in wrcmd.pdeps]
            for e in barrier_to_release:
                e.succeed()
