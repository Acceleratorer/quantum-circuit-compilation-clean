"""Preflight the fresh chemistry hybrid receipt."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    receipt = json.loads((ROOT / "experiments/exp-018/receipt.json").read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == "v23-392k-hybrid-e9cff"
    assert all(len(value) == 64 for value in receipt["member_sha256"].values())
    chemistry = receipt["member_verification"]["dfthcsos"]
    assert chemistry["status"] == "PASS"
    assert chemistry["verified_shots"] == 78080
    assert chemistry["cost"] < 297237077.4701012
    assert receipt["local_geometric_mean"] > 25.449538401211033
    assert receipt["submission_state"]["remaining_today"] == 0
    print("exp-018 receipt: PASS")

if __name__ == "__main__":
    main()
