from ..common.record import Record
from ..common.trace import Trace
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
        traces = []
        for k, v in self.records.items():
            traces.append(Trace.from_record(v))

        chrome_traces['traceEvents'] = traces
        json_string = json.dumps(chrome_traces, default=lambda o: o.__dict__, indent=4)
        with open(outpath, 'w') as outfile:
            outfile.write(json_string)