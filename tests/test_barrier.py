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


class TestBarrier(unittest.TestCase):
    def test_barrier_construction(self):
        env = simpy.Environment()
        t1 = RequestCmd('read', 'compute', 1, [0], [])
        t2 = RequestCmd('add', 'compute', 2, [], [0])
        t3 = RequestCmd('mul', 'compute', 3, [], [0])

        barr = Barrier(env, 0, 't1->t2->t3', t1, t2)
        assert barr.producer_event.triggered == False

    def test_sram_engine_barrier_read_after_write(self):
        ctx = Context(env=simpy.Environment())
        cmx = SRAM(ctx, 'ram1')
        env = ctx.env

        # issue write requests
        wcmds = []
        for i in range(3):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, [], [], i + 1)
            wcmds.append(cmd)
            env.process(cmx.request(cmd))

        # issue one barrier for last write cmd
        barr = Barrier(env, 2, 'RAW', wcmds[-1], -1)
        wcmds[-1].pdeps = [barr.id]

        # issue read request
        rcmds = []
        for i in range(3):
            rcmd = MemCmd(f'read{i}', MemOp.READ, i, [], [], i + 1)
            rcmds.append(rcmd)
            env.process(cmx.request(rcmd))
        rcmds[0].cdeps = [barr.id]
        barr.consumer = rcmds[0].id

        # add it into barrier mgr
        ctx.barrierMgr.add(barr)

        cmx.start_event.succeed()
        # env.process(cmx.run())
        ctx.env.run(until=1000)

    def test_sram_multiple_deps(self):
        ctx = Context(env=simpy.Environment(), barrierMgr=BarrierMgr())
        mgr = ctx.barrierMgr
        cmx = SRAM(ctx, 'ram1')
        env = ctx.env

        # a, b, c, d 4 tasks
        a = MemCmd(f'a', MemOp.READ, 1, [], [], 4)
        b = MemCmd(f'b', MemOp.WRITE, 2, [], [], 7)
        c = MemCmd(f'c', MemOp.READ, 3, [], [], 15)
        d = MemCmd(f'd', MemOp.READ, 4, [], [], 9)

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

    def test_sram_dead_lock(self):
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
        # b rely on edge from c to d
        b.cdeps = [bAB.id, bCD.id]
        b.pdeps = [bBC.id]
        c.cdeps = [bBC.id, bAC.id]
        c.pdeps = [bCD.id]
        d.cdeps = [bCD.id]

        cmx.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)