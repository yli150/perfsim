from .enginecmp import EngineCompute
from ..context.context import Context
import simpy
from ..common.devicedes import DeviceDesc


class DSP(EngineCompute):
    def __init__(self, context: Context, name: str) -> None:
        super().__init__(context, name)
        self.devicedes = DeviceDesc('DSP', '', 0)

    def post_init(self):
        super().post_init()
        self.prc = self.env.process(self.run())

    def run(self):
        yield self.start_event

        while True:
            cmd = yield self.cmd_in_queue.get()

            # get all the barriers which are consumed by this command
            barrier_wait_for = [self.barrierMgr.get(b).producer_event for b in cmd.cdeps]
            yield simpy.AllOf(self.env, barrier_wait_for)

            cmd.start(self.env.now)
            latency = 10
            yield self.env.timeout(latency)
            cmd.terminate(self.env.now)

            yield self.cmd_out_queue.put(cmd)

            # release barrier
            barrier_to_release = [self.barrierMgr.get(b).producer_event for b in cmd.pdeps]
            for e in barrier_to_release:
                e.succeed()