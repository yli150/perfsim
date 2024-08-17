from abc import ABC, abstractmethod
from ..context.context import Context


class Power(ABC):
    def __init__(self, context: Context, name: str, powerfile: str) -> None:
        self.ctx = context
        self.env = context.env
        self.post_init(powerfile)

    @abstractmethod
    def post_init(self, powerfile):
        pass

    @abstractmethod
    def get_power(self, voltage: int):
        pass

    @abstractmethod
    def get_leakage_power(self):
        pass
