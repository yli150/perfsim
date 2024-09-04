import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.salvesram import SlaveSRAM
from perfsim.common.command import ComputeCmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.engine.dcore import DCore
from perfsim.context.context import Context
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barrier import Barrier
from perfsim.common.command import ComputeCmd


class TestDCore(unittest.TestCase):
    def test_dcore_slavesram(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr

        dcore = DCore(ctx, 'core')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = ComputeCmd(f'a', 'MMA', 1, macs=1 * 1024)
        b = ComputeCmd(f'b', 'MMB', 2, macs=2 * 1024)
        c = ComputeCmd(f'c', 'MMC', 3, macs=3 * 1024)
        d = ComputeCmd(f'd', 'MMD', 4, macs=4 * 1024)

        for cmd in [a, b, c, d]:
            env.process(dcore.request(cmd))

        dcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()
        ctx.statistic.to_chrome_trace('dcore.json', power_trace=False)
        '''
        TaskB start from 16, 2*enqueue_cost = 16 
        1 Packet 1 Run on Device TensorCore_0 from 8 to 13
        2 Packet 2 Run on Device TensorCore_0 from 16 to 22
        3 Packet 3 Run on Device TensorCore_0 from 24 to 31
        4 Packet 4 Run on Device TensorCore_0 from 32 to 40
        
        '''