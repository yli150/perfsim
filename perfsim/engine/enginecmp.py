from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import simpy
from typing import List
from perfsim.common.packet import StatisticPacket
from perfsim.common.record import Record


class EngineCompute():
    def __init__(self, context: Context, name: str) -> None:
        self.ctx = context
        self.env = context.env
        self.barrierMgr = context.barrierMgr
        self.name = name
        self.post_init()

    def post_init(self):
        self.start_event = self.env.event()
        self.cmd_in_queue = simpy.Store(self.env)
        self.cmd_out_queue = simpy.Store(self.env)
        self.recordprc = self.env.process(self.record_into_statistic_report())

    def request(self, cmpCmd):
        yield self.cmd_in_queue.put(StatisticPacket(cmpCmd, self.devicedes))

    def record_into_statistic_report(self):
        while True:
            packet = yield self.cmd_out_queue.get()
            self.ctx.statistic.add(Record.from_packet(packet))