from abc import ABC, abstractmethod
from ..engine.enginebase import EngineBase
from ..context.context import Context
import simpy


class Memory(ABC):
    def __init__(self, context: Context, name: str) -> None:
        self.env = context.env
        self.barrierMgr = context.barrierMgr
        self.name = name
        self.post_init()

    def post_init(self):
        self.start_event = self.env.event()
        self.cmd_in_queue = simpy.Store(self.env)
        self.cmd_out_queue = simpy.Store(self.env)

    def connect_producer(self, producer: EngineBase) -> None:
        self.producer = producer

    def connect_consumer(self, consumer: EngineBase) -> None:
        self.consumer = consumer

    def run(self):
        yield self.start_event