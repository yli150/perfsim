import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.singleportsram import SinglePortSRAM
from perfsim.common.command import ComputeCmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.engine.tensorcore import TensorCore
from perfsim.context.context import Context


class TestTensorCore(unittest.TestCase):
    def test_tensorcore_run(self):
        ctx = Context(env=simpy.Environment())
        tensorcore = TensorCore(ctx, 'core')
        env = ctx.env

        for i in range(9):
            cmd = ComputeCmd(f'MM_{i}', 'MatMul', i, macs=(i + 1) * 1024)
            env.process(tensorcore.request(cmd))

        tensorcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)
        ctx.statistic.dump()
