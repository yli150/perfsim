from .memoryabc import Memory
from perfsim.context.context import Context
import simpy
from typing import List
from perfsim.common.devicedes import DeviceDesc
import logging


class SlaveRRSRAM(Memory):
    '''
    SRAM with multiple ports
    - Each Port has fixed bandwidth = 1 
    - Multiple Port can work at the same time.
    - Round Robin pattern, port 0 -> num of port 
    '''
    def __init__(self, context: Context, name: str, port_num: int) -> None:
        self.devicedes = DeviceDesc('SRAM', '', 1)
        self.port_num = port_num
        self.rr_token = 0
        super().__init__(context, name)

    def post_init(self):
        super().post_init()
        self.requestQueues = [simpy.Store(self.env, capacity=100) for i in range(self.port_num)]
        self.responseQueues = [simpy.Store(self.env, capacity=100) for i in range(self.port_num)]
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event

        while True:
            for port_id in range(self.rr_token, self.rr_token + self.port_num):
                pid = port_id % self.port_num

                wait = self.env.timeout(1)
                request = self.requestQueues[pid].get()

                # 1 cycle to used to query if any request from queue
                yield request | wait
                self.rr_token = (pid + 1) % self.port_num

                if request.triggered:
                    rdcmd = request.value
                    start = self.env.now
                    latency = max(rdcmd.size, 1) * port_id
                    yield self.env.timeout(latency)

                    print(
                        f'Device {self.name} Process {rdcmd}, Port ID {port_id}, Start from {start}  Complete at {self.env.now}'
                    )
                    yield self.responseQueues[pid].put(rdcmd)

    def request(self, memCmd, port_id: int):
        yield self.requestQueues[port_id].put(memCmd)