from .record import Record


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