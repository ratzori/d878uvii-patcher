"""
Checks the patcher against the stock firmware. The firmware isn't part of
this repository, so point D878UVII_STOCK at a stock .CDD, or at a folder of
them, to run these:

    D878UVII_STOCK=/path/to/FIRMWARE.CDD python3 -m unittest discover tests
    D878UVII_STOCK=/path/to/stock-folder python3 -m unittest discover tests

Each supported version found is tested; other files are ignored.
"""
import os
import sys
import unittest
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import d878uvii_patcher as dp  # noqa: E402
from firmware import VERSIONS, identify  # noqa: E402
from patches import ALL  # noqa: E402

STOCK = os.environ.get("D878UVII_STOCK")


def find_stock(path: Path):
    files = sorted(p for p in path.iterdir() if p.suffix.lower() == ".cdd") if path.is_dir() else [path]
    found = []
    for f in files:
        data = f.read_bytes()
        fw = identify(data)
        if fw:
            found.append((fw, data))
    return found


@unittest.skipUnless(STOCK, "set D878UVII_STOCK to a stock .CDD or a folder of them")
class TestPatcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = find_stock(Path(STOCK))
        if not cls.stock:
            raise unittest.SkipTest(f"no supported stock .CDD in {STOCK}")

    def selections(self, fw):
        ids = sorted(i for i in ALL if fw.supports(ALL[i]))
        return [set(c) for n in range(1, len(ids) + 1) for c in combinations(ids, n)]

    def test_known_outputs(self):
        for fw, stock in self.stock:
            for ids in self.selections(fw):
                with self.subTest(version=fw.version, ids=ids):
                    out = dp.build(fw, stock, [ALL[i] for i in ids])
                    self.assertEqual(dp.sha256(out), fw.known_outputs[frozenset(ids)][0])

    def test_patches_are_independent(self):
        """Each patch's hooks and code are the same as in its single-patch image; nothing else changes."""
        for fw, stock in self.stock:
            for ids in self.selections(fw):
                with self.subTest(version=fw.version, ids=ids):
                    out = dp.build(fw, stock, [ALL[i] for i in ids])
                    claimed = set()
                    for i in ids:
                        p = ALL[i]
                        single = dp.build(fw, stock, [p])
                        at = dp.placed(fw, p)
                        own = {a - fw.load_addr + j for a, _ in at.hooks for j in range(4)}
                        own |= set(range(at.code_addr - fw.load_addr, len(single)))
                        self.assertEqual([out[o] for o in sorted(own)], [single[o] for o in sorted(own)])
                        claimed |= own
                    for off in range(len(out)):
                        if off not in claimed:
                            self.assertEqual(out[off], stock[off] if off < len(stock) else 0xff)

    def test_refuses_other_firmware(self):
        for fw, stock in self.stock:
            with self.subTest(version=fw.version):
                with self.assertRaises(dp.PatchError):
                    dp.build(fw, stock[:-1] + b"\x00", [ALL["usb-fix"]])
                self.assertIsNone(identify(stock[:-1] + b"\x00"))


class TestDefinitions(unittest.TestCase):
    """Runs without any firmware."""

    def test_versions_are_unique(self):
        self.assertEqual(len({fw.sha256 for fw in VERSIONS}), len(VERSIONS))

    def test_known_outputs_cover_every_selection(self):
        for fw in VERSIONS:
            ids = sorted(i for i in ALL if fw.supports(ALL[i]))
            want = {frozenset(c) for n in range(1, len(ids) + 1) for c in combinations(ids, n)}
            self.assertEqual(set(fw.known_outputs), want, fw.version)

    def test_firmware_md_matches(self):
        """FIRMWARE.md lists every version, its stock SHA-256 and each output's SHA-256 and tested flag."""
        doc = (Path(__file__).resolve().parent.parent / "FIRMWARE.md").read_text()
        for fw in VERSIONS:
            self.assertIn(f"## {fw.version} ", doc)
            self.assertIn(fw.sha256, doc)
            for digest, tested in fw.known_outputs.values():
                self.assertIn(f"`{digest}` | {'yes' if tested else 'not yet'} |", doc)


if __name__ == "__main__":
    unittest.main()
