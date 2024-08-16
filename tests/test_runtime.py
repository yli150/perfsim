import unittest
from perfsim.common.command import RequestCmd, ComputeCmd
from perfsim.barrier.barrier import Barrier
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import simpy
from perfsim.firmware.runtime import Runtime


class TestRuntime(unittest.TestCase):
    def test_runtime_dispatch(self):

        # build context/env/tasks
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MemCmd(f'a', MemOp.READ, 1, [], [], 4)
        b = ComputeCmd(f'b', MemOp.WRITE, 2, [], [], 7 * 1024)
        c = MemCmd(f'c', MemOp.READ, 3, [], [], 15)
        d = ComputeCmd(f'd', MemOp.READ, 4, [], [], 9 * 1024)

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

        # Push task into runtime
        rt = Runtime(context=ctx, name='runtime')
        for t in [a, b, c, d]:
            rt.push(t)

        rt.start()
        env.run(until=1000)

        ctx.statistic.to_chrome_trace('x.json')
