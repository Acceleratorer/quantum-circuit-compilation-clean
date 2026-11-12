"""Small standard-library preflight for the current candidate receipt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "experiments" / "exp-015" / "receipt.json"


def main() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == "v22-392k-dqi"
    assert len(receipt["member_sha256"]) == 3
    assert receipt["local_verification"]["dqi"]["shots"] == 102400
    assert receipt["local_verification"]["dqi"]["value_errors"] == 0
    assert receipt["local_verification"]["dqi"]["phase_errors"] == 0
    assert receipt["local_verification"]["geometric_mean"] > 25.40482
    assert all(len(value) == 64 for value in receipt["member_sha256"].values())
    print("submission receipt: PASS")


if __name__ == "__main__":
    main()
