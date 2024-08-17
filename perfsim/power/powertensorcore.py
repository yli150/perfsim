from abc import ABC, abstractmethod
from .powerbase import Power
from ..context.context import Context


class PowerTensorCore(Power):
    def __init__(self, context: Context, name: str, powerfile: str) -> None:
        super().__init__(context, name, powerfile)

    def post_init(self, powerfile):
        return super().post_init(powerfile)

    def get_power(self, freq: int):
        lkage_p = self.get_leakage_power()
        dyn_p = self.get_dynamic_power(freq)
        return lkage_p + dyn_p

    def get_leakage_power(self) -> int:
        return 1.0

    def get_dynamic_power(self, freq: int) -> float:
        cdyn = 1.0  # nf
        volt = self.f2v(freq)  # freq: MHZ
        p = cdyn * volt * volt * freq  # mw
        return p

    def f2v(self, freq: int):
        return 0.75
