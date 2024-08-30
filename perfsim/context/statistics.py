from ..common.record import Record
from ..common.trace import Trace, PowerTrace
import json
from .power_trace_pti import generate_power_trace_pti


class Statistics(object):
    def __init__(self) -> None:
        self.records = []
        self.powertrace = False

    def get(self, id: int):
        for r in self.records:
            if id == r.id:
                return r

    def add(self, record: Record):
        self.records.append(record)

    def dump(self):
        for v in self.records:
            print(f'{v.id} {v}')

    def to_chrome_trace(self, outpath: str, power_trace: bool):
        chrome_traces = {}
        chrome_traces['displayTimeUnit'] = 'ns'

        # time trace and power trace
        traces = []
        for v in self.records:
            traces.append(Trace.from_record(v))

        if power_trace:
            ptraces = generate_power_trace_pti(self.records, pti=1)
            # Combine power traces and time traces
            traces.extend(ptraces)

        chrome_traces['traceEvents'] = traces
        json_string = json.dumps(chrome_traces, default=lambda o: o.__dict__, indent=4)
        with open(outpath, 'w') as outfile:
            outfile.write(json_string)