import json
from pathlib import Path


def test_exp024_receipt_has_verified_cutoff17_dqi():
    p = Path(__file__).parents[1] / "experiments" / "exp-024" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v27-syed-v12-cutoff17"
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["invsqrt.kmb"]["sha256"].startswith("321aff83")
    assert data["members"]["dqi.kmb"]["sha256"].startswith("cc0d7d25")
    assert data["members"]["dfthcsos/submission.npz"]["sha256"].startswith("33cfa061")
    assert data["official_verification_dqi"]["status"] == "PASS"
    assert data["official_verification_dqi"]["verified_shots"] == 102400
    assert data["official_verification_dqi"]["value_errors"] == 0
    assert data["official_verification_dqi"]["phase_errors"] == 0
