"""Audit a public Kaggle notebook output without executing notebook code."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import zipfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_members(notebook_path: Path) -> dict[str, str]:
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        tree = ast.parse("".join(cell.get("source", [])))
        values: dict[str, object] = {}
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {"MANIFEST", "INV_SHA"}:
                values[target.id] = ast.literal_eval(node.value)
        if "MANIFEST" in values and "INV_SHA" in values:
            members = dict(values["MANIFEST"])
            members["invsqrt.kmb"] = values["INV_SHA"]
            return members
    raise ValueError("Notebook has no literal MANIFEST and INV_SHA assignments")


def verifier_result(log_path: Path) -> tuple[dict[str, object], str]:
    events = json.loads(log_path.read_text(encoding="utf-8"))
    stdout = "".join(
        event.get("data", "")
        for event in events
        if event.get("stream_name") == "stdout"
    )
    decoder = json.JSONDecoder()
    for offset, char in enumerate(stdout):
        if char != "{":
            continue
        try:
            result, _ = decoder.raw_decode(stdout[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(result, dict) and "circuit_sha256" in result and "toffoli_count" in result:
            return result, stdout
    raise ValueError("Kaggle output log has no complete DQI verifier result")


def audit(notebook_path: Path, archive_path: Path, log_path: Path) -> dict[str, object]:
    expected = expected_members(notebook_path)
    result, stdout = verifier_result(log_path)
    with zipfile.ZipFile(archive_path) as archive:
        crc_error = archive.testzip()
        names = sorted(name for name in archive.namelist() if not name.endswith("/"))
        actual = {name: sha256_bytes(archive.read(name)) for name in names}

    extra = sorted(set(actual) - set(expected))
    missing = sorted(set(expected) - set(actual))
    mismatches = sorted(
        name for name in set(actual) & set(expected) if actual[name] != expected[name]
    )
    log_archive_hashes = re.findall(
        r"wrote .*?submission\.zip ([0-9a-f]{64})", stdout, flags=re.IGNORECASE
    )
    archive_hash = sha256_bytes(archive_path.read_bytes())
    report = {
        "notebook_sha256": sha256_bytes(notebook_path.read_bytes()),
        "output_log_sha256": sha256_bytes(log_path.read_bytes()),
        "archive_sha256": archive_hash,
        "archive_bytes": archive_path.stat().st_size,
        "archive_crc_error": crc_error,
        "expected_members": len(expected),
        "actual_members": len(actual),
        "member_sha256": actual,
        "extra_members": extra,
        "missing_members": missing,
        "hash_mismatches": mismatches,
        "logged_archive_hashes": log_archive_hashes,
        "archive_hash_matches_log": archive_hash in log_archive_hashes,
        "dqi_verifier": result,
    }
    report["hash_manifest_pass"] = not (crc_error or extra or missing or mismatches)
    report["verifier_pass"] = (
        result.get("status") == "PASS"
        and result.get("value_errors") == 0
        and result.get("phase_errors") == 0
    )
    report["archive_log_pass"] = archive_hash in log_archive_hashes
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.notebook, args.archive, args.log)
    print(json.dumps(report, indent=2, sort_keys=True))
    if not all(
        report[key]
        for key in ("hash_manifest_pass", "verifier_pass", "archive_log_pass")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
