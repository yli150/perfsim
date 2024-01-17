import unittest
from perfsim.engine.enginebase import EngineBase
from perfsim.context.simcontext import SimContext
from perfsim.common.command import RequestCmd

import simpy


class TestEngine(unittest.TestCase):
    def test_engine_run(self):
        env = simpy.Environment()
        ctx = SimContext(env)
        hw = EngineBase(env, 'device')
        ctx.attach(hw)
        cmds = [RequestCmd(f'wl_{i}', 'compute', i) for i in range(3)]
        ctx.process(cmds)
        env.run()
