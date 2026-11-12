"""Preflight the 5778cdd5 retained-product hybrid receipt."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    r = json.loads((ROOT / "experiments/exp-019/receipt.json").read_text(encoding="utf-8"))
    assert r["candidate_id"] == "v24-5778-retained-hybrid"
    assert r["dqi_sha256"].startswith("5778cdd5")
    assert r["official_verification"]["default"]["status"] == "PASS"
    assert r["official_verification"]["default"]["value_errors"] == 0
    assert r["official_verification"]["default"]["phase_errors"] == 0
    assert r["official_verification"]["s1"]["phase_errors"] == 0
    assert r["official_verification"]["s2"]["phase_errors"] == 0
    assert r["local_geometric_mean"] > 25.449539329310575
    assert all(len(v) == 64 for v in r["member_sha256"].values())
    print("exp-019 receipt: PASS")

if __name__ == "__main__":
    main()
