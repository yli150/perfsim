from dataclasses import dataclass, field
from .record import Record


@dataclass
class Trace():
    ph: str = 'X'
    name: str = "None"
    pid: int = 0
    tid: int = 0
    ts: int = 0
    dur: int = 0
    cat: str = "None"
    args: dict = field(default_factory=dict)

    @classmethod
    def from_record(cls, record):
        return cls(name=record.name,
                   pid=record.devicedes.name,
                   tid=record.devicedes.id,
                   ts=record.startT,
                   dur=record.endT - record.startT,
                   cat='MEM')


@dataclass
class PowerTrace():
    ph: str = 'C'
    name: str = "Power"
    pid: int = 0
    tid: int = 0
    ts: int = 0
    dur: int = 0
    cat: str = "None"
    args: dict = field(default_factory=dict)

    @classmethod
    def from_record(cls, record):
        return cls(name=record.devicedes.name + '_POWER',
                   pid=record.devicedes.name + '_POWER',
                   ts=record.startT,
                   dur=record.endT - record.startT,
                   args={record.devicedes.name + '_POWER': record.power})
