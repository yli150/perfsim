from ..common.record import Record
from ..common.trace import Trace, PowerTrace
import json


class Statistics(object):
    def __init__(self) -> None:
        self.records = {}
        self.powertrace = False

    def get(self, id: int):
        return self.records[id]

    def add(self, record: Record):
        self.records[record.id] = record

    def dump(self):
        for k, v in self.records.items():
            print(f'{k} {v}')

    def to_chrome_trace(self, outpath: str):
        chrome_traces = {}
        chrome_traces['displayTimeUnit'] = 'ns'

        # time trace and power trace
        traces = []
        ptraces = []

        for k, v in self.records.items():
            traces.append(Trace.from_record(v))
            if self.powertrace:
                # Generate power trace from record
                pt = PowerTrace.from_record(v)
                # insert terminal pt
                ptzero = PowerTrace(name=pt.name, pid=pt.pid, tid=pt.tid, ts=pt.ts + pt.dur, args={pt.name: 0.0})
                ptraces.append(pt)
                ptraces.append(ptzero)

        # Combine power traces and time traces
        traces.extend(ptraces)

        chrome_traces['traceEvents'] = traces
        json_string = json.dumps(chrome_traces, default=lambda o: o.__dict__, indent=4)
        with open(outpath, 'w') as outfile:
            outfile.write(json_string)