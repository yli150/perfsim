from perfsim.barrier.barriermgr import BarrierMgr
from perfsim.context.context import Context
import simpy
from typing import List
from perfsim.common.command import RequestCmd, ComputeCmd, MemCmd, DspCmd
from collections import defaultdict
from perfsim.engine.tensorcore import TensorCore
from perfsim.engine.dsp import DSP
from perfsim.memory.sram import SRAM


class Runtime():
    def __init__(self, context: Context, name: str) -> None:
        self.ctx = context
        self.env = context.env
        self.barrierMgr: BarrierMgr = context.barrierMgr
        self.name = name
        self.request_fifo = defaultdict(list)
        self.start_event = self.env.event()
        # build device instance
        self.hw_devices = {
            'memory': SRAM(self.ctx, 'SRAM'),
            'compute': TensorCore(self.ctx, 'TensorCore'),
            'dsp': DSP(self.ctx, 'DSP')
        }

    def push(self, rcmd: RequestCmd):
        if isinstance(rcmd, ComputeCmd):
            self.request_fifo['compute'].append(rcmd)
        if isinstance(rcmd, MemCmd):
            self.request_fifo['memory'].append(rcmd)
        if isinstance(rcmd, DspCmd):
            self.request_fifo['dsp'].append(rcmd)

    def start(self):
        '''
        Kick of processing once all tasks are pushed into request fifo 
        '''
        self.start_event.succeed()
        for _, dev in self.hw_devices.items():
            dev.start_event.succeed()
        self.env.process(self._process())

    def _process(self):
        '''
        For each engine, spawn one process to handle 
        '''
        yield self.start_event

        for engine, tasks in self.request_fifo.items():
            if engine == 'compute':
                self.env.process(self._compute())
            if engine == 'memory':
                self.env.process(self._dma())
            if engine == 'dsp':
                self.env.process(self._dsp())

    def _compute(self):
        yield self.start_event
        tasks = self.request_fifo['compute']
        dev = self.hw_devices['compute']
        for task in tasks:
            self.env.process(dev.request(task))

    def _dma(self):
        yield self.start_event
        tasks = self.request_fifo['memory']
        dev = self.hw_devices['memory']
        for task in tasks:
            self.env.process(dev.request(task))

    def _dsp(self):
        yield self.start_event
        tasks = self.request_fifo['dsp']
        dev = self.hw_devices['dsp']
        for task in tasks:
            self.env.process(dev.request(task))