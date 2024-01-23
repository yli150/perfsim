import unittest
from perfsim.engine.enginebase import EngineBase
from perfsim.engine.enginemulstage import EngineMulStage
from perfsim.engine.enginessync import EngineSync

from perfsim.context.simcontext import SimContext
from perfsim.common.command import RequestCmd
from perfsim.barrier.barrier import Barrier
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import simpy


class TestStatistic(unittest.TestCase):
    def test_sram_multiple_deps(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr
        cmx = SRAM(ctx, 'ram1')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MemCmd(f'a', MemOp.READ, 1, 4)
        b = MemCmd(f'b', MemOp.WRITE, 2, 7)
        c = MemCmd(f'c', MemOp.READ, 3, 15)
        d = MemCmd(f'd', MemOp.READ, 4, 9)

        for cmd in [a, b, c, d]:
            env.process(cmx.request(cmd))

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
        b.cdeps = [bAB.id]
        b.pdeps = [bBC.id]
        c.cdeps = [bBC.id, bAC.id]
        c.pdeps = [bCD.id]
        d.cdeps = [bCD.id]

        cmx.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()

        assert ctx.statistic.get(d.id).startT == 4 + 14 + 15
        assert ctx.statistic.get(d.id).endT == 4 + 14 + 15 + 9
