from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Firmware:
    name: str                       # stock file name without extension
    version: str
    sha256: str                     # of the stock .CDD; nothing else is accepted
    load_addr: int                  # where the .CDD is loaded in flash
    spi_length_at: int              # offset of the .CDD length in the .spi
    cdi_length_at: int              # offset of the .CDD length in the .CDI
    symbols: dict                   # {name: value} used by the patches (see each patch's NEEDS)
    known_outputs: dict             # {frozenset(patch ids): (output .CDD SHA-256, tested on a radio)}

    def supports(self, patch) -> bool:
        return all(n in self.symbols for n in patch.needs)
