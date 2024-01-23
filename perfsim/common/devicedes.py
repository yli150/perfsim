from dataclasses import dataclass, field


@dataclass
class DeviceDesc:
    name: str
    type: str
    id: int

    def __str__(self) -> str:
        return f'{self.name}_{self.id}'