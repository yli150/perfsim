from typing import List
from simpy import Event


class Barrier(object):
    def __init__(self, env, id: int, name: str, producer: 'RequestCmd', consumer: 'RequestCmd') -> None:
        self.env = env
        self.id = id
        self.name = name
        self.consumer = consumer
        self.producer = producer
        self.post_init()

    def post_init(self):
        self.producer_event = self.env.event()
