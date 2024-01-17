import simpy 
from typing import List
from ..common.command import RequestCmd

class SimContext:

    def __init__(self, env) -> None:
        self.env = env 
        self.timeout = 100 
        self.engines = []

    def attach(self, engine):
        self.engines.append(engine)

    def schedule(self, cmds:List[RequestCmd]):
        yield self.scheduler_start_event 
        for cmd in cmds:
            yield self.engines[0].cmd_in_queue.put(cmd)
        yield self.env.timeout(10)

    def monitor(self):
        start = self.env.now 
        yield self.moniter_event
        qstatus = [engine.cmd_out_queue for engine in self.engines]
        while True:
            for taskq in qstatus:
                if taskq.items:
                    yield taskq.get()
            yield self.env.timeout(5)

            end = self.env.now 
            # exceeds the timeout, break the monitor process 
            if end - start > self.timeout:
                break 

        
    def process(self, cmds:List[RequestCmd]):
        self.scheduler_start_event = self.env.event()
        self.moniter_event = self.env.event()
        self.env.process(self.schedule(cmds))
        self.env.process(self.monitor())

        # start all engines 
        for engine in self.engines:
            engine.start_event.succeed()

        # start moniter 
        self.moniter_event.succeed()

        # start scheduler 
        self.scheduler_start_event.succeed()
