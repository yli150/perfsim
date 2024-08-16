from perfsim.common.command import RequestCmd
import simpy
from ..context.context import Context
from .enginecmp import EngineCompute
from ..common.devicedes import DeviceDesc


class EngineMulStage(EngineCompute):
    '''
    3 Stages 
    Load -> Compute -> Store 
    '''
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('DSP', '', 0)
        self.post_init()

    def post_init(self):
        super().post_init()

        # 3 queues
        self.loadQ = simpy.Store(self.env, capacity=1)
        self.computeQ = simpy.Store(self.env, capacity=1)
        self.storeQ = simpy.Store(self.env, capacity=1)

        self.cmd_in_queue = simpy.Store(self.env, capacity=1)
        self.cmd_out_queue = simpy.Store(self.env, capacity=1)

        # process
        self.env.process(self.load())
        self.env.process(self.compute())
        self.env.process(self.store())
        self.env.process(self.run())

    def cycles(self, cmd: RequestCmd):
        return cmd.id + 2

    def full(self):
        return len(self.cmd_in_queue) >= 1

    def run(self):
        yield self.start_event

    def load(self):
        while True:
            cmd = yield self.cmd_in_queue.get()
            cycle = 2
            print(f'Device {self.name} load {cmd},  takes {cycle} to process at {self.env.now}')
            yield self.env.timeout(cycle)
            yield self.loadQ.put(cmd)

    def compute(self):
        while True:
            cmd = yield self.loadQ.get()
            cycle = 3
            print(f'Device {self.name} compute {cmd},  takes {cycle} to process at {self.env.now}')
            yield self.env.timeout(cycle)
            yield self.storeQ.put(cmd)

    def store(self):
        while True:
            cmd = yield self.storeQ.get()
            cycle = 4
            print(f'Device {self.name} store {cmd},  takes {cycle} to process at {self.env.now}')
            yield self.env.timeout(cycle)
            yield self.cmd_out_queue.put(cmd.id)