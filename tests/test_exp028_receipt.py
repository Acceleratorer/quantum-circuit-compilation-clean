import json
from pathlib import Path


def test_exp028_receipt_pins_verified_helios_chemistry():
    p = Path(__file__).parents[1] / "experiments" / "exp-028" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["candidate_id"] == "v31-helios-v116b-chemistry"
    assert data["archive_sha256"].startswith("19f6880d")
    assert data["member_count"] == 18
    assert data["zip_test"] is True
    assert data["members"]["dfthcsos/submission.npz"]["sha256"].startswith("865f52ce")
    assert data["chemistry_verification"]["status"] == "PASS"
    assert data["chemistry_verification"]["verified_shots"] == 78080
    assert data["retained_component_verification"]["dqi"]["value_errors"] == 0
    assert data["retained_component_verification"]["dqi"]["phase_errors"] == 0
    assert data["submission"]["attempted"] is False
