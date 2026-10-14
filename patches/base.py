from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Placed:
    code_addr: int                  # where the patch code is placed (after the stock image)
    code: str                       # Thumb-2 assembly, assembled at code_addr
    hooks: list                     # [(address, one 4-byte instruction)] written into the stock code
    entries: dict = field(default_factory=dict)  # {address: expected bytes} for extra entry points


@dataclass
class Patch:
    id: str
    title: str
    needs: tuple                    # symbol names a firmware version must define to support this patch
    place: Callable                 # place(symbols) -> Placed; symbols has exactly the names in needs


def lo(v):
    return v & 0xffff


def hi(v):
    return v >> 16
