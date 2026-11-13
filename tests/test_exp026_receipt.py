import json
from pathlib import Path


def test_exp026_receipt_has_composed_dqi_pin():
    p = Path(__file__).parents[1] / "experiments" / "exp-026" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v29-syed-v12-cutoff17-retained"
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["dqi.kmb"]["sha256"].startswith("c60beda8")
    assert data["official_verification_dqi"]["status"] == "PASS"
    assert data["official_verification_dqi"]["verified_shots"] == 102400
    assert data["official_verification_dqi"]["value_errors"] == 0
    assert data["official_verification_dqi"]["phase_errors"] == 0
