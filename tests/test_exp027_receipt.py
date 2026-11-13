import json
from pathlib import Path


def test_exp027_receipt_has_cutoff18_areebbb_dqi_pin():
    p = Path(__file__).parents[1] / "experiments" / "exp-027" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v30-areebbb-cutoff18-retained"
    assert data["archive_sha256"].startswith("86e4300c")
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["dqi.kmb"]["sha256"].startswith("821bf8d1")
    assert data["official_verification_dqi"]["status"] == "PASS"
    assert data["official_verification_dqi"]["verified_shots"] == 102400
    assert data["official_verification_dqi"]["value_errors"] == 0
    assert data["official_verification_dqi"]["phase_errors"] == 0
    assert data["submission_ref"] == "58299178"
