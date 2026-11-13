import json
from pathlib import Path


def test_exp029_receipt_pins_kirderf_portfolio():
    p = Path(__file__).parents[1] / "experiments" / "exp-029" / "receipt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["experiment"] == "exp-029"
    assert data["candidate"] == "kirderf-27.11056-portfolio"
    assert data["archive"]["sha256"].startswith("dce2b52d")
    assert data["archive"]["member_count"] == 18
    assert data["archive"]["zip_test"] is True
    assert data["chemistry"]["status"] == "PASS"
    assert data["chemistry"]["verified_shots"] == 78080
    assert data["dqi"]["value_errors"] == 0
    assert data["dqi"]["phase_errors"] == 0
    assert data["submission"]["attempted"] is False


