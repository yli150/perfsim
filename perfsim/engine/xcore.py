from .enginecmp import EngineCompute
from ..context.context import Context
import simpy
from ..common.devicedes import DeviceDesc
from ..power.powertensorcore import PowerTensorCore
from typing import List
from ..common.command import MemCmd, MemOp


class XCore(EngineCompute):
    def __init__(self, context: Context, name: str, sram_reqQ: simpy.Store, sram_resQ: simpy.Store) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('XCore', '', 0)
        # SRAM Request and Response Queue
        self.sram_reqQ = sram_reqQ
        self.sram_resQ = sram_resQ

    def post_init(self):
        super().post_init()
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event

        while True:
            cmd = yield self.cmd_in_queue.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in cmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            # record start time
            cmd.start(self.env.now)

            # load data from sram
            yield self.env.process(self.read_data_blocking(size=cmd.macs))

            # self.read_data_blocking(size=cmd.macs)
            # add compute latency
            latency = cmd.macs // 1024
            yield self.env.timeout(latency)
            cmd.terminate(self.env.now)

            yield self.cmd_out_queue.put(cmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in cmd.pdeps]
            for e in barrier_to_release:
                e.succeed()

    def read_data_blocking(self, size: int) -> simpy.Event:
        # construct a MemCmd
        # ack = self.env.event()
        memorycmd = MemCmd('sram_read', type=MemOp.READ, id=-1, size=size // 128)
        yield self.sram_reqQ.put(memorycmd)
        res = yield self.sram_resQ.get()
        # ack.succeed()
        return res
