from dataclasses import dataclass


@dataclass
class Stencil:
    H: int
    W: int
    C: int
    K: int
