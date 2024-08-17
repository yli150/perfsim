from .packet import StatisticPacket


class Record(object):
    @classmethod
    def from_packet(cls, packet: StatisticPacket):
        return cls(packet.id, packet.name, packet.devicedes, packet.startT, packet.endT, packet.power)

    def __init__(self, id: int, name: str, devicedes: 'DeviceDes', startT: int, endT: int, power: float) -> None:
        self.id = id
        self.name = name
        self.devicedes = devicedes
        self.startT = startT
        self.endT = endT
        self.power = power

    def __str__(self) -> str:
        return f'Packet {self.id} Run on Device {self.devicedes} from {self.startT} to {self.endT}'