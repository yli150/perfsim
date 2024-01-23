class Record(object):
    @classmethod
    def from_packet(cls, packet: 'Packet'):
        return cls(packet.id, packet.device_id, packet.startT, packet.endT)

    def __init__(self, id: int, device_id: int, startT: int, endT: int) -> None:
        self.id = id
        self.device_id = device_id
        self.startT = startT
        self.endT = endT

    def __str__(self) -> str:
        return f'Packet {self.id} Run on Device {self.device_id} from {self.startT} to {self.endT}'