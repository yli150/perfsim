import unittest
from perfsim.memory.salvesram import SlaveSRAM
from perfsim.memory.singleportsram import SinglePortSRAM
from perfsim.common.command import MemCmd, MemOp
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import logging


class TestSlaveMultiplePortSRAM(unittest.TestCase):
    def test_slave_sram_run(self):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ctx = Context(env=simpy.Environment())
        cmx = SlaveSRAM(ctx, 'ram1', port_num=4)
        env = ctx.env

        for i in range(17):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, size=i + 1)
            env.process(cmx.request(cmd, port_id=i % cmx.port_num))

        cmx.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)
