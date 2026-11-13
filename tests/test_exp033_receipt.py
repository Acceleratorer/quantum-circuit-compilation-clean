import json
from pathlib import Path


def test_exp033_receipt_is_self_consistent():
    root = Path(__file__).parents[1]
    receipt = json.loads((root / "experiments/exp-033/receipt.json").read_text(encoding="utf-8"))
    assert receipt["archive"]["sha256"] == "0f992a97d4411737cb1da2712b3617f0bdfd784ce3a5b3ebe8689fd85a2365cb"
    assert receipt["archive"]["member_count"] == 18
    assert receipt["members"]["dfthcsos/submission.npz"].startswith("06d67d21dbfe")
    assert receipt["dfthcsos"]["verified_shots"] == 78080
    assert receipt["dfthcsos"]["status"] == "PASS"
    assert receipt["portfolio"]["local_zero_failure_gm"] > receipt["portfolio"]["previous_best_gm"]
