import json
from pathlib import Path


def test_exp022_receipt_has_public_pins():
    p = Path(__file__).parents[1] / "experiments" / "exp-022" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v25-syed-own-v12"
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["invsqrt.kmb"]["sha256"].startswith("321aff83")
    assert data["members"]["dqi.kmb"]["sha256"].startswith("7cbe8ecf")
    assert data["members"]["dfthcsos/submission.npz"]["sha256"].startswith("6418ec8e")
