import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.singleportsram import SinglePortSRAM
from perfsim.common.command import ComputeCmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.engine.tensorcore import TensorCore
from perfsim.context.context import Context
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barrier import Barrier
from perfsim.common.command import ComputeCmd


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

    def test_tensorcore_sram(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr
        sram = SRAM(ctx, 'ram1')
        tensorcore = TensorCore(ctx, 'core')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MemCmd(f'a', MemOp.READ, 1, size=4)
        b = MemCmd(f'b', MemOp.READ, 2, size=7)
        c = ComputeCmd(f'c', 'MM', 3, macs=4 * 1024)
        d = MemCmd(f'd', MemOp.READ, 4, size=9)

        for cmd in [a, b, d]:
            env.process(sram.request(cmd))

        for cmd in [c]:
            env.process(tensorcore.request(cmd))

        # dependency
        # a --> b --- \
        #   \----------> c ----> d

        bAB = Barrier(env, 10, 'ab', producer=a.id, consumer=b.id)
        bAC = Barrier(env, 11, 'ac', producer=a.id, consumer=c.id)
        bBC = Barrier(env, 12, 'bc', producer=b.id, consumer=c.id)
        bCD = Barrier(env, 13, 'cd', producer=c.id, consumer=d.id)
        for barrier in [bAB, bAC, bBC, bCD]:
            mgr.add(barrier)

        # assign deps on command
        a.pdeps = [bAB.id, bAC.id]
        # b rely on edge from c to d
        b.cdeps = [bAB.id]
        b.pdeps = [bBC.id]
        c.cdeps = [bBC.id, bAC.id]
        c.pdeps = [bCD.id]
        d.cdeps = [bCD.id]

        sram.start_event.succeed()
        tensorcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()
        ctx.statistic.to_chrome_trace('x2.json')