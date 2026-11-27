"""Static audit for the public H8 search script.

This intentionally parses source only. It never imports or executes the
downloaded notebook/script, embedded archive, generators, or circuits.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "external" / "qcc-prv-h8-live-search-v3.py"
OUT = ROOT.parent.parent / "evals" / "2026-11-28-exp093-h8-search-audit.json"


def literal_assignments(tree: ast.AST) -> dict[str, object]:
    values: dict[str, object] = {}
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        if value is None:
            continue
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, TypeError, SyntaxError):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                values[target.id] = parsed
    return values


def main() -> None:
    source_text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(SOURCE))
    values = literal_assignments(tree)

    # Search only for declarations. Runtime verifier reads are not evidence
    # of a declared score or cost, so exclude those source lines explicitly.
    declaration_lines = [
        line
        for line in source_text.splitlines()
        if "REF =" not in line and "v.get(" not in line and "r2[" not in line
    ]
    declaration_text = "\n".join(declaration_lines)
    budget_match = re.search(r"H8_BUDGET[\"']\s*,\s*[\"'](\d+)[\"']", source_text)
    explicit_claims = sorted(
        set(
            re.findall(
                r"(?im)\b(?:lb|leaderboard|chem(?:istry)?[_ ]?cost|toffoli|score)\b\s*[:=]\s*[-+]?\d+(?:\.\d+)?",
                declaration_text,
            )
        )
    )

    result = {
        "experiment": "exp-093",
        "status": "closed_no_go_gate",
        "source": "toshiaki517/qcc-prv-h8-live-search-v3",
        "source_path": str(SOURCE.relative_to(ROOT.parent.parent)),
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "source_line_count": len(source_text.splitlines()),
        "static_parse": True,
        "executed_downloaded_code": False,
        "private_kernel_launched": False,
        "declared_budget_seconds": int(budget_match.group(1)) if budget_match else values.get("BUDGET"),
        "declared_loaders": values.get("LOADERS"),
        "declared_reference_constants": values.get("REF"),
        "explicit_score_or_cost_claims": explicit_claims,
        "declared_chemistry_cost": None,
        "declared_lb": None,
        "baseline_chem_cost": 249_853_852.96,
        "required_chem_cost": 204_476_813.83,
        "required_reduction_pct": 18.16,
        "gate_cleared": False,
        "decision": "No credible near-gate resource or cost estimate is present; stochastic search output would only be known after a private kernel run.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
