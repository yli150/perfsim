from .packet import StatisticPacket


class Record(object):
    @classmethod
    def from_packet(cls, packet: StatisticPacket):
        return cls(packet.id, packet.name, packet.device_id, packet.startT, packet.endT)

    def __init__(self, id: int, name: str, device_id: int, startT: int, endT: int) -> None:
        self.id = id
        self.name = name
        self.device_id = device_id
        self.startT = startT
        self.endT = endT

    def __str__(self) -> str:
        return f'Packet {self.id} Run on Device {self.device_id} from {self.startT} to {self.endT}'