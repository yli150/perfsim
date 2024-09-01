import unittest
from perfsim.memory.salvesram import SlaveSRAM
from perfsim.memory.sram_rr import SlaveRRSRAM
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
        mmx = SlaveSRAM(ctx, 'ram1', port_num=4)
        env = ctx.env

        for i in range(17):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, size=i + 1)
            env.process(mmx.request(cmd, port_id=i % mmx.port_num))

        mmx.start_event.succeed()
        # env.process(mmx.run())
        env.run(until=1000)

    def test_rr_slave_sram_run(self):

        ctx = Context(env=simpy.Environment())
        mmx = SlaveRRSRAM(ctx, 'ram1', port_num=4)
        env = ctx.env

        cmds = []
        cmds.append((MemCmd(f'write{0}', MemOp.WRITE, 1, size=1 + 1), 0))
        cmds.append((MemCmd(f'write{1}', MemOp.WRITE, 3, size=2 + 1), 2))
        cmds.append((MemCmd(f'write{2}', MemOp.WRITE, 2, size=3 + 1), 1))
        cmds.append((MemCmd(f'write{3}', MemOp.WRITE, 4, size=4 + 1), 3))

        for cmd, port in cmds:
            env.process(mmx.request(cmd, port_id=port))

        mmx.start_event.succeed()
        # env.process(mmx.run())
        env.run(until=1000)

    def test_rr_slave_sram_run_traffic(self):

        ctx = Context(env=simpy.Environment())
        mmx = SlaveRRSRAM(ctx, 'ram1', port_num=4)
        env = ctx.env

        cmds = []
        cmds.append((MemCmd(f'write', MemOp.WRITE, 1, size=1 + 1), 0))
        cmds.append((MemCmd(f'write', MemOp.WRITE, 3, size=2 + 1), 2))
        cmds.append((MemCmd(f'write', MemOp.WRITE, 2, size=3 + 1), 1))
        cmds.append((MemCmd(f'write', MemOp.WRITE, 4, size=4 + 1), 3))
        cmds.append((MemCmd(f'write', MemOp.WRITE, 5, size=5 + 1), 0))

        for cmd, port in cmds:
            env.process(mmx.request(cmd, port_id=port))

        mmx.start_event.succeed()
        # env.process(mmx.run())
        env.run(until=1000)
        '''
        Expected log. 
        Device ram1 Process MemCmd write_1_WRITE_2, Port ID 0, Start from 0  Complete at 0
        Device ram1 Process MemCmd write_2_WRITE_4, Port ID 1, Start from 0  Complete at 4
        Device ram1 Process MemCmd write_3_WRITE_3, Port ID 2, Start from 4  Complete at 10
        Device ram1 Process MemCmd write_4_WRITE_5, Port ID 3, Start from 10  Complete at 25
        Device ram1 Process MemCmd write_5_WRITE_6, Port ID 0, Start from 25  Complete at 25
        '''

    def test_rr_slave_sram_run_wait_timeout(self):

        ctx = Context(env=simpy.Environment())
        mmx = SlaveRRSRAM(ctx, 'ram1', port_num=4)
        env = ctx.env

        cmds = []
        # b will start from timeout*4
        cmds.append((MemCmd(f'a', MemOp.WRITE, 1, size=1 + 1), 1))
        cmds.append((MemCmd(f'b', MemOp.WRITE, 3, size=2 + 1), 1))

        for cmd, port in cmds:
            env.process(mmx.request(cmd, port_id=port))

        mmx.start_event.succeed()
        # env.process(mmx.run())
        env.run(until=1000)
        '''
        Expected log. 
        Device ram1 Process MemCmd a_1_WRITE_2, Port ID 1, Start from 1  Complete at 3
        Device ram1 Process MemCmd b_3_WRITE_3, Port ID 1, Start from 6  Complete at 9
        '''