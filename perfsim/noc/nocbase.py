from abc import ABC, abstractmethod
from ..engine.enginebase import EngineBase
from ..context.context import Context
import simpy


class NocBase(ABC):
    def __init__(self, context: Context, name: str, num_ports: int) -> None:
        self.ctx = context
        self.env = context.env
        self.barrierMgr = context.barrierMgr
        self.name = name
        self.num_ports = num_ports
        self.post_init()

    def post_init(self):
        # for each connected node, in command queue and output command queue
        self.start_event = self.env.event()
        self.cmd_in_queue = [simpy.Store(self.env) for p in range(self.num_ports)]
        self.cmd_out_queue = [simpy.Store(self.env) for p in range(self.num_ports)]

    def run(self):
        yield self.start_event