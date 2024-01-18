import unittest
from perfsim.memory.sram import SRAM
from perfsim.common.command import MemCmd, MemOp
import simpy


class TestSRAM(unittest.TestCase):
    def test_sram_run(self):
        env = simpy.Environment()
        cmx = SRAM(env, 'ram1')

        cmds = []
        for i in range(9):
            cmd = MemCmd(f'write{i}', MemOp.WRITE, i, i + 1)
            cmds.append(cmd)

        # issue request at the begin
        for i in range(5):
            cmd = MemCmd(f'read{i}', MemOp.READ, i, i + 1)
            cmds.append(cmd)

        cmx.start_event.succeed()
        env.process(cmx.run(cmds))
        env.run(until=1000)
