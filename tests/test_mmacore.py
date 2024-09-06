import unittest
from perfsim.common.command import MMACmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.engine.mmacore import MMACore
from perfsim.context.context import Context
from perfsim.common.command import ComputeCmd


class TestMmaCore(unittest.TestCase):
    def test_mmacore_single_block(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr

        dcore = MMACore(ctx, 'core')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MMACmd(f'a', 'MMA', 1, n=32, m=32, k=32)

        for cmd in [a]:
            env.process(dcore.request(cmd))

        dcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()
        ctx.statistic.to_chrome_trace('mma.json', power_trace=False)
        # load 16, compute 16 , store 8
        assert ctx.statistic.records[0].endT == 40

    def test_mmacore_blocks(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr

        dcore = MMACore(ctx, 'core')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MMACmd(f'a', 'MMA', 1, n=128, m=32, k=32)

        for cmd in [a]:
            env.process(dcore.request(cmd))

        dcore.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

        ctx.statistic.dump()
        ctx.statistic.to_chrome_trace('mmax.json', power_trace=False)
        # load , compute 16 , store 8
        assert ctx.statistic.records[0].endT == 16 + 16 * 4 + 8
