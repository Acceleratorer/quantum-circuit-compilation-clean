"""Parse one public Kaggle notebook without executing any notebook code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


BASELINE_CHEM_COST = 249_853_852.96
REQUIRED_CHEM_COST = 204_476_813.83
REQUIRED_REDUCTION_PCT = 18.16


def _read_payload(notebook: Path) -> tuple[dict, list[dict]]:
    raw = notebook.read_bytes()
    cells = json.loads(raw.decode("utf-8"))["cells"]
    code = "\n".join("".join(cell.get("source", [])) for cell in cells if cell["cell_type"] == "code")
    match = re.search(r"D\s*=\s*json\.loads\(r?\"\"\"(.*?)\"\"\"\)", code, re.DOTALL)
    if not match:
        raise ValueError("could not find the notebook's static D payload")
    return json.loads(match.group(1)), cells


def audit(notebook: Path) -> dict:
    payload, cells = _read_payload(notebook)
    markdown = "\n".join("".join(cell.get("source", [])) for cell in cells if cell["cell_type"] == "markdown")
    metadata_path = notebook.parent / "kernel-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    chem_cost = float(payload["chem_cost"])
    reduction_pct = (BASELINE_CHEM_COST - chem_cost) / BASELINE_CHEM_COST * 100
    return {
        "experiment": "exp-092",
        "status": "closed_no_go_gate",
        "notebook": "goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-29000",
        "notebook_path": str(notebook),
        "notebook_sha256": hashlib.sha256(notebook.read_bytes()).hexdigest(),
        "cell_count": len(cells),
        "declared_lb": payload["lb"],
        "declared_chem_cost": chem_cost,
        "declared_required_chem_cost": REQUIRED_CHEM_COST,
        "baseline_chem_cost": BASELINE_CHEM_COST,
        "chemistry_reduction_pct": reduction_pct,
        "required_reduction_pct": REQUIRED_REDUCTION_PCT,
        "declared_toffoli_counts": payload["T"],
        "declared_lambda_eff": payload["lam"],
        "declared_license": "Apache-2.0" if "Apache-2.0" in markdown else None,
        "declared_kernel_sources": metadata.get("kernel_sources", []),
        "declared_competition_sources": metadata.get("competition_sources", []),
        "executed_downloaded_code": False,
        "private_kernel_launched": False,
        "gate_cleared": chem_cost <= REQUIRED_CHEM_COST,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.notebook)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
