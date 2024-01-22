from typing import List
from simpy import Event


class Barrier(object):
    def __init__(self, env, id: int, name: str, producer: List['RequestCmd'], consumers: List['RequestCmd']) -> None:
        self.env = env
        self.id = id
        self.name = name
        self.consumers = consumers
        self.producer = producer
        self.post_init()

    def post_init(self):
        self.consumer_cnt = len(self.consumers)
        self.producer_cnt = len(self.producer)
        self.consumer_event = self.env.event()
        self.producer_event = self.env.event()

    def decrement_consumer(self):
        if self.consumer_cnt <= 0:
            raise RuntimeError(f'{self} consumer event already triggered')
        self.consumer_cnt -= 1
        self.consumer_event.succeed()

    def decrement_producer(self):
        if self.producer_cnt <= 0:
            raise RuntimeError(f'{self} producer event already triggered')
        self.producer_cnt -= 1
        if self.producer_cnt == 0:
            self.producer_event.succeed()
