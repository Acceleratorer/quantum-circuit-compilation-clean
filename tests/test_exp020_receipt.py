"""Preflight the rejected 328ced chemistry experiment receipt."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    receipt = json.loads((ROOT / "experiments/exp-020/receipt.json").read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == "chem-328ced-3045-static"
    assert receipt["official_verification"]["status"] == "PASS"
    assert receipt["official_verification"]["verified_shots"] == 78080
    assert receipt["official_verification"]["score"] == 302196075.2036132
    assert receipt["comparison"]["candidate_local_geometric_mean"] < receipt["comparison"]["v24_local_geometric_mean"]
    assert receipt["decision"] == "REJECT"
    assert receipt["archive_created"] is False
    assert len(receipt["factorization_sha256"]) == 64
    assert all(len(value) == 64 for value in receipt["member_sha256"].values())
    print("exp-020 receipt: PASS")


if __name__ == "__main__":
    main()
