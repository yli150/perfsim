import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.salvesram import SlaveSRAM
from perfsim.common.command import ComputeCmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.engine.xcore import XCore
from perfsim.context.context import Context
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barrier import Barrier
from perfsim.common.command import ComputeCmd


class TestXCore(unittest.TestCase):
    def test_xcore_slavesram(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr

        sram = SlaveSRAM(ctx, 'ram1', port_num=8)
        xcore = XCore(ctx, 'core', sram.requestQueues[1], sram.responseQueues[1])
        env = ctx.env

        # a, b, c, d 4 tasks
        a = ComputeCmd(f'a', 'MMA', 1, macs=1 * 1024)
        b = ComputeCmd(f'b', 'MMB', 2, macs=2 * 1024)
        c = ComputeCmd(f'c', 'MMC', 3, macs=3 * 1024)
        d = ComputeCmd(f'd', 'MMD', 4, macs=4 * 1024)

        for cmd in [a, b, c, d]:
            env.process(xcore.request(cmd))

        sram.start_event.succeed()
        xcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()
        ctx.statistic.to_chrome_trace('xcore.json', power_trace=False)