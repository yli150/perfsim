from perfsim.common.command import MMACmd
import simpy
from ..context.context import Context
from .enginecmp import EngineCompute
from ..common.devicedes import DeviceDesc
from dataclasses import dataclass, field


@dataclass
class MMABlock():
    bid: int
    m: int
    n: int
    k: int
    src: MMACmd
    last: bool = field(default=False)
    first: bool = field(default=False)


class MMACore(EngineCompute):
    '''
    3 Stages 
    - Load -> Compute -> Store 
    - Partition MM to blocks.
    '''
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('DSP', '', 0)
        self.post_init()

    def post_init(self):
        super().post_init()

        # 3 queues
        self.loadQ = simpy.Store(self.env, capacity=1)
        self.computeQ = simpy.Store(self.env, capacity=10)
        self.storeQ = simpy.Store(self.env, capacity=10)

        self.load_event = self.env.event()

        self.cmd_in_queue = simpy.Store(self.env, capacity=10)
        self.cmd_out_queue = simpy.Store(self.env, capacity=10)

        # process
        self.env.process(self.load())
        self.env.process(self.compute())
        self.env.process(self.store())
        self.env.process(self.run())

    def run(self):
        yield self.start_event

        while True:
            cmd: MMACmd = yield self.cmd_in_queue.get()
            # partition into blocks
            blocks = self.partition(cmd)
            for block in blocks:
                yield self.loadQ.put(block)
                # use event to wait for data processed by self.load
                yield self.load_event
                self.load_event = self.env.event()

    def partition(self, cmd: MMACmd):
        m_block, n_block, k_block = 32, 32, 32
        blocks = []
        idx = 0
        for _m in range(0, cmd.m, m_block):
            for _n in range(0, cmd.n, n_block):
                for _k in range(0, cmd.k, k_block):
                    blocks.append(MMABlock(idx, m_block, n_block, k_block, src=cmd))
                    idx += 1
        # flag first and last block
        blocks[0].first = True
        blocks[-1].last = True
        return blocks

    def load(self):
        yield self.start_event
        while True:
            block: MMABlock = yield self.loadQ.get()
            lsize = block.m * block.k
            lsize += block.n * block.k
            cycle = lsize // (128)
            yield self.env.timeout(cycle)
            self.load_event.succeed()
            yield self.computeQ.put(block)

    def compute(self):
        while True:
            block: MMABlock = yield self.computeQ.get()
            compute = block.m * block.n * block.k
            cycle = compute // 2048
            yield self.env.timeout(cycle)
            yield self.storeQ.put(block)

    def store(self):
        while True:
            block: MMABlock = yield self.storeQ.get()
            ssize = block.n * block.m
            cycle = ssize // (128)
            yield self.env.timeout(cycle)
            if block.last:
                block.src.terminate(self.env.now)
                yield self.cmd_out_queue.put(block.src)
