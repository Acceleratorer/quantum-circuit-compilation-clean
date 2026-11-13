import json
from pathlib import Path


def test_exp031_receipt_is_self_consistent():
    root = Path(__file__).parents[1]
    receipt = json.loads((root / "experiments/exp-031/receipt.json").read_text(encoding="utf-8"))
    assert receipt["archive"]["sha256"] == "2040d92d2a479916e88672251257f05b05d806b8e4f82852b1812bdc9328d024"
    assert receipt["archive"]["member_count"] == 18
    assert receipt["invsqrt"]["verified_shots"] == 200540928
    assert receipt["dqi"]["verified_shots"] == 102400
    assert receipt["dqi"]["value_errors"] == 0
    assert receipt["dqi"]["phase_errors"] == 0
    assert receipt["dfthcsos"]["verified_shots"] == 78080
    assert receipt["portfolio"]["local_zero_failure_gm"] > receipt["portfolio"]["previous_best_gm"]
