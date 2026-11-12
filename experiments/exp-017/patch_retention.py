"""Reproduce Pablo Diego's 392k DQI retention patch.

Usage: python patch_retention.py BASE.kmx OUT.kmx
The resulting KMX is converted to KMB with kickmix and checked against the
expected SHA-256 in the experiment receipt.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path

REPLACES = {
    51515666: "CCX q12 q828 q861\nCX q861 q860\n",
    51515696: "CCX q12 q828 q858\nCX q858 q860\n",
    51522444: "CX q862 q860\nHMR q862 b101418\nCZ q12 q828 if b101418\n",
    51522474: "CX q857 q860\nHMR q857 b101419\nCZ q12 q828 if b101419\n",
}
INSERTS = {
    51518086: "CX q858 q857\nCX q857 q858\n",
    51519115: "CX q861 q862\nCX q862 q861\n",
}
EXPECTED_KMB_SHA256 = "64d0c2f9e0d677d588791b9d00b19edaf518aabf7e95214c50a03f685ee2ea56"

def patch(base: Path, out: Path) -> None:
    seen: set[int] = set()
    with base.open("r", encoding="utf-8", newline="") as fin, out.open("w", encoding="utf-8", newline="") as fout:
        for idx, line in enumerate(fin, 1):
            if idx in REPLACES:
                fout.write(REPLACES[idx]); seen.add(idx)
            else:
                fout.write(line)
                if idx in INSERTS:
                    fout.write(INSERTS[idx]); seen.add(idx)
    assert seen == set(REPLACES) | set(INSERTS), seen

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: patch_retention.py BASE.kmx OUT.kmx")
    patch(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"patched {sys.argv[2]}")
