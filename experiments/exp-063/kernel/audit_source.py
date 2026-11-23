"""Audit the pinned Syed v25 DQI source tree without executing its code."""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import re


DATASET = Path("/kaggle/input/datasets/syed3000/vqcc-own-circuit-portfolio")
PACKAGE = DATASET / "dqi_generator" / "dqi_generator"
SOURCE = PACKAGE / "vendor" / "d70-source"
OUT = Path("/kaggle/working/exp063-source-audit")
EXPECTED_ARCHIVE_SHA256 = "54fcce0d9846afae1fde0330e69803e4d9633a4e1ac4fcac49a7d1413ad20b45"
EXPECTED_PACKAGE_SHA256 = {
    "README.md": "8c43097e3fa875365894d370e10e5ce79fb186a5c74bc76170f0e69250db974b",
    "build.py": "d400f69a899a7aac23d6abb5ed257c1cdbe96c192b964240d82e3022a4c497a9",
    "emit.py": "0e69f89841f30db5b2254ae4bfdf455ca0f2de3087f803b6f8fc5b6ec84ca11c",
    "lower_fredkin.py": "f7c9168e85490bd2747e13d0e7216c3ca5ebc0d47864827bf310984250d3ebfe",
    "manifest.json": "d6a8fa8169eacfa50bcc43f89affd64a9fc2368002a367477b21b8824bcd3483",
    "LICENSE": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "NOTICE": "b4e1cd477cca2cb53254e80ae35357b5609ddb61c4f10a0c724e107c1fdae042",
}
EXPECTED_PROFILE = "paired-plain"
EXPECTED_OUTPUT_SHA256 = "fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5"
FORBIDDEN_CIRCUIT_SUFFIXES = {".kmb", ".kmx"}
STATIC_PATTERNS = {
    "network": re.compile(r"(?i)\b(requests|urllib\.request|urlopen|socket|httpx|aiohttp)\b"),
    "credentials": re.compile(r"(?i)\b(KAGGLE_API_TOKEN|KAGGLE_KEY|KAGGLE_USERNAME|API_TOKEN|PASSWORD)\b"),
    "shell_execution": re.compile(r"(?i)(os\.system\s*\(|shell\s*=\s*True|Popen\s*\()"),
    "subprocess": re.compile(r"\bsubprocess\.(run|call|Popen|check_call|check_output)\s*\("),
    "dynamic_execution": re.compile(r"\b(exec|eval)\s*\("),
    "pickle": re.compile(r"\bpickle\.(load|loads)\s*\("),
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree_digest(root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
    return digest.hexdigest()


def locate_competition_root() -> tuple[Path, Path]:
    matches = [
        path for path in Path("/kaggle/input").rglob("verify_submission_dqi.py")
        if path.parent.name == "dqi"
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected one official DQI verifier, found {len(matches)}")
    verifier = matches[0]
    root = verifier.parent.parent.parent
    if not (root / "kickmix" / "kickmix.so").is_file():
        raise RuntimeError(f"official Kickmix extension missing under {root}")
    return root, verifier


def audit():
    if OUT.exists():
        raise RuntimeError(f"fresh audit path expected: {OUT}")
    if not PACKAGE.is_dir() or not SOURCE.is_dir():
        raise RuntimeError(f"version 17 DQI source tree missing under {DATASET}")

    package_hashes = {name: sha256(PACKAGE / name) for name in EXPECTED_PACKAGE_SHA256}
    if package_hashes != EXPECTED_PACKAGE_SHA256:
        raise RuntimeError(f"upstream package hash mismatch: {package_hashes}")

    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("archive_sha256") != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("upstream source archive claim changed")
    expected_files = manifest["files"]
    source_entries = list(SOURCE.rglob("*"))
    symlinks = [path.relative_to(SOURCE).as_posix() for path in source_entries if path.is_symlink()]
    if symlinks:
        raise RuntimeError(f"symlinks are not allowed in the pinned source tree: {symlinks[:8]}")
    source_files = sorted(path for path in source_entries if path.is_file())
    actual_names = {path.relative_to(SOURCE).as_posix() for path in source_files}
    if actual_names != set(expected_files):
        raise RuntimeError(
            f"extracted tree file list differs from manifest: "
            f"missing={sorted(set(expected_files) - actual_names)[:5]}, "
            f"extra={sorted(actual_names - set(expected_files))[:5]}"
        )
    bad_hashes = {
        name: (expected_files[name], sha256(SOURCE / name))
        for name in sorted(expected_files)
        if sha256(SOURCE / name) != expected_files[name]
    }
    if bad_hashes:
        raise RuntimeError(f"source file hash mismatch: {list(bad_hashes.items())[:5]}")
    forbidden = [
        path.relative_to(SOURCE).as_posix()
        for path in source_files
        if path.suffix.lower() in FORBIDDEN_CIRCUIT_SUFFIXES
    ]
    if forbidden:
        raise RuntimeError(f"compiled circuit files present in source tree: {forbidden[:8]}")

    findings = {key: [] for key in STATIC_PATTERNS}
    python_files = [path for path in source_files if path.suffix.lower() == ".py"]
    for path in python_files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for name, pattern in STATIC_PATTERNS.items():
                if pattern.search(line):
                    findings[name].append({
                        "path": path.relative_to(SOURCE).as_posix(),
                        "line": line_no,
                        "text": line.strip()[:240],
                    })

    competition_root, verifier = locate_competition_root()
    competition_files = {}
    for upstream, host in manifest["competition_files"].items():
        path = competition_root / host
        if not path.is_file():
            raise RuntimeError(f"official competition input missing: {host}")
        competition_files[upstream] = {
            "host_path": host,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }

    profile_hash = manifest.get("outputs", {}).get(EXPECTED_PROFILE)
    if profile_hash != EXPECTED_OUTPUT_SHA256:
        raise RuntimeError(f"published output hash changed: {profile_hash}")
    tree_sha = tree_digest(SOURCE, source_files)
    suffixes = collections.Counter(path.suffix.lower() or "[none]" for path in source_files)
    return {
        "status": "SOURCE_STATIC_AUDIT_COMPLETE_NO_CODE_EXECUTED",
        "dataset": "syed3000/vqcc-own-circuit-portfolio",
        "dataset_version": 17,
        "license": "Apache-2.0",
        "package_hashes": package_hashes,
        "source_archive_sha256_claim": EXPECTED_ARCHIVE_SHA256,
        "source_archive_present": (PACKAGE / "vendor" / "d70-source.zip").is_file(),
        "source_tree_files": len(source_files),
        "source_tree_bytes": sum(path.stat().st_size for path in source_files),
        "source_tree_sha256": tree_sha,
        "source_tree_digest": "sha256 over sorted relative path, NUL, file SHA-256, newline",
        "source_tree_suffixes": dict(sorted(suffixes.items())),
        "compiled_circuit_inputs_read": False,
        "compiled_circuit_files_in_source_tree": forbidden,
        "profile": EXPECTED_PROFILE,
        "published_output_sha256": profile_hash,
        "official_verifier_path": str(verifier),
        "competition_root": str(competition_root),
        "competition_input_files": competition_files,
        "python_source_files": len(python_files),
        "static_scan_findings": findings,
        "static_scan_executed_code": False,
    }


def main():
    report = audit()
    OUT.mkdir(parents=True)
    (OUT / "source_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
