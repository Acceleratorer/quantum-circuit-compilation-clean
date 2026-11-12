"""Preflight the rejected 1f19ecca7044 chemistry receipt."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    receipt = json.loads((ROOT / "experiments/exp-021/receipt.json").read_text(encoding="utf-8"))
    assert receipt["candidate_id"] == "chem-1f19ecca7044-4132-static"
    official = receipt["official_verification"]
    assert official["status"] == "PASS"
    assert official["verified_shots"] == 78080
    assert official["score"] == 298998656.7697932
    assert official["toffoli_count"] == 14926.0
    assert receipt["comparison"]["candidate_local_geometric_mean"] < receipt["comparison"]["v24_local_geometric_mean"]
    assert receipt["decision"] == "REJECT"
    assert receipt["archive_created"] is False
    assert len(receipt["member_sha256"]) == 16
    assert all(len(value) == 64 for value in receipt["member_sha256"].values())
    print("exp-021 receipt: PASS")


if __name__ == "__main__":
    main()
