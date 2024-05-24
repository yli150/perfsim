import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.singleportsram import SinglePortSRAM
from perfsim.common.command import ComputeCmd
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.noc.nocpe import NocPE
from perfsim.context.context import Context
from perfsim.memory.sram import SRAM, MemCmd, MemOp
from perfsim.barrier.barrier import Barrier
from perfsim.common.command import XferCmd


class TestNoc(unittest.TestCase):
    def test_noc_run(self):
        ctx = Context(env=simpy.Environment())
        noc = NocPE(ctx, 'noc', num_ports=4)
        env = ctx.env

        cmds = []
        cmds.append(XferCmd(name=f'MM', type='NOC', id=0, size=10 * 4, src=0, dst=1))
        cmds.append(XferCmd(name=f'MM', type='NOC', id=1, size=10 * 4, src=0, dst=2))
        cmds.append(XferCmd(name=f'MM', type='NOC', id=2, size=10 * 4, src=2, dst=3))
        cmds.append(XferCmd(name=f'MM', type='NOC', id=3, size=10 * 4, src=2, dst=0))

        for cmd in cmds:
            env.process(noc.request(cmd))

        noc.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)
        ctx.statistic.dump()
