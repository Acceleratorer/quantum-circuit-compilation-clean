import json
from pathlib import Path


def test_exp032_receipt_is_self_consistent():
    root = Path(__file__).parents[1]
    receipt = json.loads((root / "experiments/exp-032/receipt.json").read_text(encoding="utf-8"))
    assert receipt["archive"]["sha256"] == "8a56b17df9fe0d9abeb10b60f5f21a76924158256b3338b438c7200c1f382937"
    assert receipt["archive"]["member_count"] == 18
    assert receipt["members"]["dfthcsos/submission.npz"].startswith("bdd3cd1df1b5")
    assert receipt["dfthcsos"]["verified_shots"] == 78080
    assert receipt["dfthcsos"]["status"] == "PASS"
    assert receipt["portfolio"]["local_zero_failure_gm"] > receipt["portfolio"]["previous_best_gm"]
