from .enginecmp import EngineCompute
from ..context.context import Context
import simpy
from ..common.devicedes import DeviceDesc
from simpy import Store, Container, Resource


class DCore(EngineCompute):
    '''
    - For any request, insert a req overhead 
    - For any response, insert a singnal overhead 

    '''
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('TensorCore', '', 0)

    def post_init(self):
        super().post_init()
        self.token = Resource(self.env, capacity=1)
        self.reqQ = Store(self.env)
        self.resQ = Store(self.env)
        self.enqueue_cost = 8
        self.dequeue_cost = 4
        self.prc = self.env.process(self.run())
        self.inprc = self.env.process(self.income())
        self.computeprc = self.env.process(self.compute())
        self.outprc = self.env.process(self.outcome())

    def income(self):
        yield self.start_event

        while True:
            cmd = yield self.cmd_in_queue.get()

            # Assume only one token comes at once
            with self.token.request() as token:
                yield token
                yield self.env.timeout(self.enqueue_cost)
                cmd.start(self.env.now)
                yield self.reqQ.put(cmd)

    def compute(self):
        yield self.start_event

        while True:
            cmd = yield self.reqQ.get()
            latency = cmd.macs // 1024
            yield self.env.timeout(latency)
            yield self.resQ.put(cmd)

    def outcome(self):
        yield self.start_event
        while True:
            cmd = yield self.resQ.get()
            # dequeue
            self.env.process(self.dequeue(cmd, self.dequeue_cost))

    def run(self):
        yield self.start_event

    def enqueue(self, cmd, latency: int):
        cmd.start(self.env.now)
        yield self.env.timeout(latency)
        yield self.reqQ.put(cmd)

    def dequeue(self, cmd, latency: int):
        yield self.env.timeout(latency)
        cmd.terminate(self.env.now)
        yield self.cmd_out_queue.put(cmd)