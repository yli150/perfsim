from abc import ABC, abstractmethod
from .nocbase import NocBase
from ..context.context import Context
import simpy
from ..common.command import XferCmd


class NocPE(NocBase):
    def post_init(self):
        super().post_init()
        self.build_rt_table()
        self.reqProcess = [self.env.process(self.slave_port_req_handler(i)) for i in range(self.num_ports)]

    def build_rt_table(self):
        # Table {src, dst} : cost [abs(dst) - abs(src)]
        rt_table = {}
        num_ports = self.num_ports
        for src in range(num_ports):
            for dst in range(num_ports):
                rt_table[(src, dst)] = abs(src - dst)

        self.rt_table = rt_table

    def run(self):
        yield self.start_event

    def request(self, memCmd: XferCmd):
        yield self.cmd_in_queue[memCmd.src].put(memCmd)

    def slave_port_req_handler(self, port: int):
        yield self.start_event
        while True:
            cmd_in_queue = self.cmd_in_queue[port]
            cmd_out_queue = self.cmd_out_queue[port]

            cmd = yield cmd_in_queue.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in cmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            ts = self.env.now
            eff = self.rt_table[(cmd.src, cmd.dst)]
            latency = cmd.size * eff
            yield self.env.timeout(latency)
            te = self.env.now

            print(f'{cmd} from {ts} to {te}')

            yield cmd_out_queue.put(cmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in cmd.pdeps]
            for e in barrier_to_release:
                e.succeed()