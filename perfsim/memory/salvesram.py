from .memoryabc import Memory
from perfsim.context.context import Context
import simpy
from typing import List
from perfsim.common.devicedes import DeviceDesc
import logging


class SlaveSRAM(Memory):
    '''
    SRAM with multiple ports
    - Each Port has fixed bandwidth = 1 
    - Multiple Port can work at the same time.
    
    '''
    def __init__(self, context: Context, name: str, port_num: int) -> None:
        self.devicedes = DeviceDesc('SRAM', '', 1)
        self.port_num = port_num
        super().__init__(context, name)

    def post_init(self):
        super().post_init()
        self.requestQueues = [simpy.Store(self.env, capacity=100) for i in range(self.port_num)]
        self.responseQueues = [simpy.Store(self.env, capacity=100) for i in range(self.port_num)]
        self.prc = [self.env.process(self.port_process(port_id=i)) for i in range(self.port_num)]

    def run(self):
        yield self.start_event

    def request(self, memCmd, port_id: int):
        yield self.requestQueues[port_id].put(memCmd)

    def port_process(self, port_id: int):
        in_queue = self.requestQueues[port_id]
        out_queue = self.responseQueues[port_id]
        while True:
            rdcmd = yield in_queue.get()

            latency = max(rdcmd.size, 1) * port_id
            yield self.env.timeout(latency)

            print(f'Device {self.name} Process {rdcmd}, Complete at {self.env.now}')
            yield out_queue.put(rdcmd)