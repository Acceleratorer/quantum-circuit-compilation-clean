import json
from pathlib import Path


def test_exp025_receipt_has_areebbb_dqi_pin():
    p = Path(__file__).parents[1] / "experiments" / "exp-025" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v28-syed-v12-areebbb-retained"
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["dqi.kmb"]["sha256"].startswith("0958baa6")
    assert data["official_source_receipt_dqi"]["status"] == "PASS"
    assert data["official_source_receipt_dqi"]["verified_shots"] == 102400
    assert data["official_source_receipt_dqi"]["value_errors"] == 0
    assert data["official_source_receipt_dqi"]["phase_errors"] == 0
