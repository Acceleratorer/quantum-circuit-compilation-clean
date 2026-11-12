import json
from pathlib import Path


def test_exp023_receipt_has_refined_chemistry_pin():
    p = Path(__file__).parents[1] / "experiments" / "exp-023" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v26-syed-v12-refined-chemistry"
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["archive_sha256"].startswith("3f2d8d70")
    assert data["members"]["invsqrt.kmb"]["sha256"].startswith("321aff83")
    assert data["members"]["dqi.kmb"]["sha256"].startswith("7cbe8ecf")
    assert data["members"]["dfthcsos/submission.npz"]["sha256"].startswith("33cfa061")
    assert data["official_verification"]["chemistry"]["status"] == "PASS"
