from ..common.trace import Trace, PowerTrace
from ..common.record import Record
import collections
import copy


def generate_power_trace_pti(records: dict, pti=1) -> dict:
    ptraces = collections.defaultdict(list)
    vrecords = copy.deepcopy(records)
    time_stamp = 0

    while (time_stamp < vrecords[-1].endT):
        for v in vrecords:
            v: Record
            if time_stamp >= v.startT and time_stamp < v.endT:
                pt = PowerTrace.from_record(v)
                pt.ts = time_stamp
            else:
                # default one with zero power
                pt = PowerTrace(name=v.devicedes.name + '_POWER',
                                pid=v.devicedes.name + '_POWER',
                                ts=time_stamp,
                                args={'power': 0.0})
            ptraces[pt.pid].append(pt)
        time_stamp += pti

    # dict to list
    xtraces = []
    for k, v in ptraces.items():
        for trace in v:
            xtraces.append(trace)

    return xtraces
