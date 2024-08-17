from ..common.record import Record
from ..common.trace import Trace, PowerTrace
import json


class Statistics(object):
    def __init__(self) -> None:
        self.records = {}

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
        last_ts = 0
        pt_dev = set()
        for k, v in self.records.items():
            traces.append(Trace.from_record(v))
            pt = PowerTrace.from_record(v)
            pt_dev.add(pt.name)
            ptraces.append(pt)
            last_ts = v.endT if v.endT > last_ts else last_ts

        # For each power device, add terminal power trace
        for _pdev in pt_dev:
            _pt = PowerTrace(name=_pdev, pid=_pdev, ts=last_ts, args={_pdev: 0.0})
            ptraces.append(_pt)

        # Combine power traces and time traces
        traces.extend(ptraces)

        chrome_traces['traceEvents'] = traces
        json_string = json.dumps(chrome_traces, default=lambda o: o.__dict__, indent=4)
        with open(outpath, 'w') as outfile:
            outfile.write(json_string)