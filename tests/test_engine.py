import unittest
from perfsim.engine.enginebase import EngineBase
from perfsim.engine.enginemulstage import EngineMulStage
from perfsim.engine.enginessync import EngineSync

from perfsim.context.simcontext import SimContext
from perfsim.common.command import RequestCmd
from perfsim.barrier.barriermgr import BarrierMgr

import simpy


class TestEngine(unittest.TestCase):
    def test_engine_run(self):
        env = simpy.Environment()
        ctx = SimContext(env)

        hw_num = 4
        for i in range(hw_num):
            hw = EngineBase(env, f'device_{i}')
            ctx.attach(hw)

        jobs_num = 16
        cmds = [RequestCmd(f'wl_{i}', 'compute', i) for i in range(jobs_num)]
        ctx.process(cmds)
        env.run()

    def test_multiple_stage_engine(self):
        env = simpy.Environment()
        ctx = SimContext(env)
        hw = EngineMulStage(env, 'hw')
        ctx.attach(hw)

        jobs_num = 8
        cmds = [RequestCmd(f'wl_{i}', 'compute', i) for i in range(jobs_num)]
        ctx.process(cmds)
        env.run()

    def test_engine_sync(self):
        env = simpy.Environment()
        ctx = SimContext(env)
        hw = EngineSync(env, 'hw')
        ctx.attach(hw)

        jobs_num = 8
        cmds = [RequestCmd(f'wl_{i}', 'dsp', i) for i in range(jobs_num)]
        ctx.process(cmds)
        env.run()