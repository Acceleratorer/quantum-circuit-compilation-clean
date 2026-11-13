import json
from pathlib import Path


def test_exp030_records_no_local_replacement():
    p = Path(__file__).parents[1] / "evals" / "2026-11-13-somejoint-sweep.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data["chemistry_sweep"]) == 6
    assert min(x["score"] for x in data["chemistry_sweep"]) > data["best_existing_chemistry_score"]
    assert len(data["dqi_static_inventory"]) == 7
