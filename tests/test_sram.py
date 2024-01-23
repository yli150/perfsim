import unittest
from perfsim.memory.sram import SRAM
from perfsim.memory.singleportsram import SinglePortSRAM
from perfsim.common.command import MemCmd, MemOp
import simpy
from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context


class TestSRAM(unittest.TestCase):
    def test_sram_run(self):
        ctx = Context(env=simpy.Environment())
        cmx = SRAM(ctx, 'ram1')
        env = ctx.env

        for i in range(9):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, size=i + 1)
            env.process(cmx.request(cmd))

        # issue request at the begin
        for i in range(5):
            cmd = MemCmd(f'read{i}', MemOp.READ, i, size=i + 1)
            env.process(cmx.request(cmd))

        cmx.start_event.succeed()
        # env.process(cmx.run())
        env.run(until=1000)

    def test_single_direct_ram_run(self):
        ctx = Context(env=simpy.Environment())
        mmx = SinglePortSRAM(ctx, 'ram1')
        env = ctx.env

        for i in range(9):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, [], [], i + 1)
            env.process(mmx.request(cmd))

        # issue request at the begin
        for i in range(5):
            cmd = MemCmd(f'read{i}', MemOp.READ, i, [], [], i + 1)
            env.process(mmx.request(cmd))

        mmx.start_event.succeed()
        env.run(until=1000)
