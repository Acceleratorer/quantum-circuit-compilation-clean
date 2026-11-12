"""Preflight the current hybrid candidate receipt without requiring binaries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "experiments" / "exp-016" / "receipt.json"


def main() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == "v22-392k-hybrid"
    assert len(receipt["member_sha256"]) == 3
    assert all(len(value) == hashlib.sha256().digest_size * 2 for value in receipt["member_sha256"].values())
    assert receipt["member_verification"]["dqi"]["value_errors"] == 0
    assert receipt["member_verification"]["dqi"]["phase_errors"] == 0
    assert receipt["local_geometric_mean"] > 25.41253
    assert receipt["submission_state"]["remaining_today"] == 0
    print("hybrid receipt: PASS")


if __name__ == "__main__":
    main()
