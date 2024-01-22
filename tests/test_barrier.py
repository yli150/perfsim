import unittest
from perfsim.engine.enginebase import EngineBase
from perfsim.engine.enginemulstage import EngineMulStage
from perfsim.engine.enginessync import EngineSync

from perfsim.context.simcontext import SimContext
from perfsim.common.command import RequestCmd
from perfsim.barrier.barrier import Barrier
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barriermgr import BarrierMgr
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
        env = simpy.Environment()
        mgr = BarrierMgr()
        cmx = SRAM(env, mgr, 'ram1')

        # issue write requests
        wcmds = []
        for i in range(3):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, i + 1)
            wcmds.append(cmd)
            env.process(cmx.request(cmd))

        # issue one barrier for last write cmd
        barr = Barrier(env, 2, 'RAW', wcmds[-1], -1)
        wcmds[-1].pdeps = [barr.id]

        # issue read request
        rcmds = []
        for i in range(3):
            rcmd = MemCmd(f'read{i}', MemOp.READ, i, i + 1)
            rcmds.append(rcmd)
            env.process(cmx.request(rcmd))
        rcmds[0].cdeps = [barr.id]
        barr.consumer = rcmds[0].id

        # add it into barrier mgr
        mgr.add(barr)

        cmx.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)