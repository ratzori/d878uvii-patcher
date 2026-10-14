#!/usr/bin/env python3
"""
Applies selectable patches to the AnyTone D878UVII firmware.

The input is an unmodified, supported firmware set (.CDD + .spi + .CDI) as
downloaded from AnyTone; its version is identified by the .CDD's SHA-256 and
anything else is refused. The output is a new three-file set. Input files are
only read.

    python3 d878uvii_patcher.py --list
    python3 d878uvii_patcher.py FIRMWARE.CDD --ptt-lock --usb-fix [--out DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

from firmware import VERSIONS, identify
from patches import ALL

try:
    from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
except ImportError:
    sys.exit("ERROR: needs the 'keystone-engine' package (pip install keystone-engine).")


class PatchError(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assemble(ks, text: str, addr: int) -> bytes:
    return bytes(ks.asm(text, addr)[0])


def placed(fw, patch):
    """Where and how the patch goes into this firmware version."""
    if not fw.supports(patch):
        raise PatchError(f"--{patch.id} isn't available for {fw.version}")
    return patch.place(SimpleNamespace(**{n: fw.symbols[n] for n in patch.needs}))


def build(fw, stock: bytes, selected: list) -> bytes:
    """Return the patched .CDD for the given firmware version, stock .CDD and patches."""
    if sha256(stock) != fw.sha256:
        raise PatchError(f"not the unmodified {fw.name}.CDD")
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    load = fw.load_addr
    stock_end = load + len(stock)
    regions, writes = [], []
    for p in selected:
        at = placed(fw, p)
        code = assemble(ks, at.code, at.code_addr)
        for addr, expected in at.entries.items():
            if code[addr - at.code_addr:][:len(expected)] != expected:
                raise PatchError(f"{p.id}: entry point {addr:#010x} is misplaced")
        if at.code_addr < stock_end:
            raise PatchError(f"{p.id}: code address {at.code_addr:#010x} is inside the stock image")
        regions.append((at.code_addr, at.code_addr + len(code), f"{p.id} code"))
        writes.append((at.code_addr, code))
        for addr, ins in at.hooks:
            hook = assemble(ks, ins, addr)
            if len(hook) != 4 or not load <= addr <= stock_end - 4:
                raise PatchError(f"{p.id}: bad hook at {addr:#010x}")
            regions.append((addr, addr + 4, f"{p.id} hook"))
            writes.append((addr, hook))

    regions.sort()
    for (a0, a1, a), (b0, b1, b) in zip(regions, regions[1:]):
        if b0 < a1:
            raise PatchError(f"{a} ({a0:#x}-{a1:#x}) overlaps {b} ({b0:#x}-{b1:#x})")

    img = bytearray(stock)
    img += b"\xff" * (max([stock_end] + [r[1] for r in regions]) - stock_end)
    for addr, data in writes:
        img[addr - load:addr - load + len(data)] = data
    return bytes(img)


def set_length(sidecar: bytes, offset: int, old_len: int, new_len: int) -> bytes:
    """The .spi and .CDI files each declare the .CDD length."""
    if int.from_bytes(sidecar[offset:offset + 4], "little") != old_len:
        raise PatchError("a .spi/.CDI file doesn't match the .CDD")
    return sidecar[:offset] + new_len.to_bytes(4, "little") + sidecar[offset + 4:]


def sibling(cdd: Path, ext: str) -> Path:
    for p in cdd.parent.iterdir():
        if p.stem == cdd.stem and p.suffix.lower() == ext.lower():
            return p
    raise PatchError(f"missing {cdd.stem}{ext} next to {cdd.name}")


def unsupported(cdd_path: Path, stock: bytes) -> str:
    supported = "\n".join(f"  {fw.name}.CDD  SHA-256 {fw.sha256}" for fw in VERSIONS)
    return (f"{cdd_path.name} is not a supported, unmodified firmware (SHA-256 {sha256(stock)}).\n"
            f"Other versions aren't supported, and an already patched file can't be patched again.\n"
            f"Supported:\n{supported}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("firmware", nargs="?", type=Path, help="the stock .CDD (its .spi and .CDI must be next to it)")
    for p in ALL.values():
        ap.add_argument(f"--{p.id}", action="append_const", dest="ids", const=p.id, help=p.title)
    ap.add_argument("--all", action="store_true", help="apply every patch available for this firmware")
    ap.add_argument("--out", type=Path, default=Path("patched"), help="output directory (default: ./patched)")
    ap.add_argument("--list", action="store_true", help="list the patches and the versions they're available for")
    args = ap.parse_args()

    if args.list:
        for p in ALL.values():
            versions = ", ".join(fw.version for fw in VERSIONS if fw.supports(p))
            print(f"  --{p.id:10} {p.title}  [{versions}]")
        return
    if args.firmware is None or not (args.all or args.ids):
        ap.error("give the stock .CDD and at least one patch (see --list)")

    try:
        cdd_path = args.firmware
        stock = cdd_path.read_bytes()
        fw = identify(stock)
        if fw is None:
            raise PatchError(unsupported(cdd_path, stock))
        ids = sorted(i for i in ALL if fw.supports(ALL[i])) if args.all else sorted(set(args.ids))
        if not ids:
            raise PatchError(f"no patches are available for {fw.version} yet")
        spi, cdi = sibling(cdd_path, ".spi").read_bytes(), sibling(cdd_path, ".CDI").read_bytes()

        patched = build(fw, stock, [ALL[i] for i in ids])
        spi = set_length(spi, fw.spi_length_at, len(stock), len(patched))
        cdi = set_length(cdi, fw.cdi_length_at, len(stock), len(patched))

        name = f"{cdd_path.stem}_" + "_".join(i.upper() for i in ids)
        outputs = [(args.out / f"{name}{ext}", data) for ext, data in ((".CDD", patched), (".spi", spi), (".CDI", cdi))]
        for path, _ in outputs:
            if path.exists():
                raise PatchError(f"{path} already exists")
    except (OSError, PatchError) as e:
        sys.exit(f"ERROR: {e}")

    args.out.mkdir(parents=True, exist_ok=True)
    for path, data in outputs:
        path.write_bytes(data)
        print(f"wrote {path}")

    print(f"\nfirmware: {fw.version}")
    print(f"patches: {', '.join(ids)}")
    print(f"SHA-256: {sha256(patched)}")
    known, tested = fw.known_outputs.get(frozenset(ids), (None, False))
    if known and known != sha256(patched):
        print("WARNING: this differs from the expected output for this selection. Don't flash it.")
    elif tested:
        print("This is the exact image that was tested on a radio.")
    else:
        print("Note: this combination hasn't been tested on a radio yet.")


if __name__ == "__main__":
    main()
