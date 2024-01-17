from perfsim.common.command import RequestCmd
import simpy


class EngineBase():
    def __init__(self, env, name: str) -> None:
        self.env = env
        self.name = name
        self.post_init()

    def post_init(self):
        self.start_event = self.env.event()
        self.cmd_in_queue = simpy.Store(self.env, capacity=1)
        self.cmd_out_queue = simpy.Store(self.env, capacity=1)
        self.proc = self.env.process(self.run())

    def cycles(self, cmd: RequestCmd):
        return cmd.id + 2

    def run(self):
        yield self.start_event

        while True:
            cmd = yield self.cmd_in_queue.get()
            cycle = self.cycles(cmd)
            print(f'recv {cmd} and takes {cycle} to process')
            yield self.env.timeout(cycle)
            yield self.cmd_out_queue.put(cmd.id)
