from .memoryabc import Memory
from ..engine.enginebase import EngineBase
from perfsim.common.command import MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import simpy
from typing import List
from perfsim.common.packet import StatisticPacket
from perfsim.common.record import Record
from perfsim.common.devicedes import DeviceDesc


class SRAM(Memory):
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('SRAM', '', 1)

    def post_init(self):
        super().post_init()
        self.readQ = simpy.Store(self.env, capacity=10)
        self.writeQ = simpy.Store(self.env, capacity=10)
        self.readprc = self.env.process(self.read())
        self.writeprc = self.env.process(self.write())
        self.recordprc = self.env.process(self.record_into_statistic_report())
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event

    def request(self, memCmd):
        if memCmd.type == MemOp.READ:
            yield self.readQ.put(StatisticPacket(memCmd, self.devicedes))
        if memCmd.type == MemOp.WRITE:
            yield self.writeQ.put(StatisticPacket(memCmd, self.devicedes))

    def read(self):
        while True:
            rdcmd = yield self.readQ.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in rdcmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            rdcmd.start(self.env.now)
            latency = max(rdcmd.size, 1)
            yield self.env.timeout(latency)
            rdcmd.terminate(self.env.now)

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

            wrcmd.start(self.env.now)

            latency = wrcmd.size * 2
            yield self.env.timeout(latency)

            wrcmd.terminate(self.env.now)

            yield self.cmd_out_queue.put(wrcmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in wrcmd.pdeps]
            for e in barrier_to_release:
                e.succeed()

    def record_into_statistic_report(self):
        while True:
            packet = yield self.cmd_out_queue.get()
            self.ctx.statistic.add(Record.from_packet(packet))