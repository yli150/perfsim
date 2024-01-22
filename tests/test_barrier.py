import unittest
from perfsim.engine.enginebase import EngineBase
from perfsim.engine.enginemulstage import EngineMulStage
from perfsim.engine.enginessync import EngineSync

from perfsim.context.simcontext import SimContext
from perfsim.common.command import RequestCmd
from perfsim.barrier.barrier import Barrier

import simpy


class TestBarrier(unittest.TestCase):
    def test_barrier_construction(self):
        env = simpy.Environment()
        t1 = RequestCmd('read', 'compute', 1, [0], [])
        t2 = RequestCmd('add', 'compute', 2, [], [0])
        t3 = RequestCmd('mul', 'compute', 3, [], [0])

        barr = Barrier(env, 0, 't1->t2->t3', [t1], [t2, t3])

        barr.decrement_producer()
        assert barr.producer_cnt == 0
        assert barr.producer_event.triggered == True
