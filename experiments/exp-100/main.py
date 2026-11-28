"""Build Diana v150 DQI source and run Google's official verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time


SOURCE_DATASET = "dziyanavalenta/q2026-v150-dqi-generator"
SOURCE_ARCHIVE_NAME = "dqi_source_targz.bin"
EXPECTED_CIRCUIT_SHA256 = "4426ca10776fcfaf3ecb75211a812a68c37228f0d3f95fd1207383d5a308deca"
EXPECTED_VERIFIER_SHA256 = "f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65"
EXPECTED_KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
LEADER_SCORE = 34.77295
BASELINE_PROJECTION = 31.798180509655666
BASELINE_DQI_COST = 336559961203.1761


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def find_one(root: Path, name: str) -> Path:
    matches = [p for p in root.rglob(name) if p.is_file()]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {name}, found {len(matches)}")
    return matches[0]


def write_result(output: Path, result: dict) -> None:
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


def main() -> None:
    started = time.monotonic()
    output = Path("/kaggle/working/exp100")
    if output.exists():
        raise RuntimeError(f"refusing to reuse {output}")
    output.mkdir(parents=True)

    input_root = Path("/kaggle/input")
    archive = find_one(input_root, SOURCE_ARCHIVE_NAME)
    verifier = find_one(input_root, "verify_submission_dqi.py")
    competition = verifier.parents[2]
    kickmix = find_one(input_root, "kickmix.so")
    if not verifier.is_file() or not kickmix.is_file():
        raise RuntimeError("official competition inputs are missing")
    if sha256_file(verifier) != EXPECTED_VERIFIER_SHA256:
        raise RuntimeError("official verifier hash mismatch")
    if sha256_file(kickmix) != EXPECTED_KICKMIX_SHA256:
        raise RuntimeError("official kickmix hash mismatch")

    run_root = Path(tempfile.mkdtemp(prefix="exp100-diana-v150-"))
    source_root = run_root / "source"
    source_root.mkdir()
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(source_root)
    archive_root = source_root / "dqi_source"
    build_output = run_root / "build-output"
    build = subprocess.run(
        [sys.executable, "-B", str(archive_root / "build.py"), str(build_output)],
        cwd=archive_root,
        capture_output=True,
        text=True,
        timeout=7200,
    )
    (output / "build.stdout.log").write_text(build.stdout, encoding="utf-8")
    (output / "build.stderr.log").write_text(build.stderr, encoding="utf-8")
    candidate = build_output / "dqi.kmb"
    if build.returncode or not candidate.is_file():
        result = {
            "experiment": "exp-100",
            "status": "SOURCE_BUILD_FAILED",
            "exit_code": build.returncode,
            "build_stdout_tail": build.stdout[-4000:],
            "build_stderr_tail": build.stderr[-4000:],
        }
        write_result(output, result)
        raise RuntimeError("v150 source build failed")

    candidate_sha = sha256_file(candidate)
    (output / "dqi.kmb").write_bytes(candidate.read_bytes())
    if candidate_sha != EXPECTED_CIRCUIT_SHA256:
        result = {
            "experiment": "exp-100",
            "status": "SOURCE_OUTPUT_HASH_MISMATCH",
            "candidate_sha256": candidate_sha,
            "expected_sha256": EXPECTED_CIRCUIT_SHA256,
            "build_log": json.loads((build_output / "dqi_build_log.json").read_text()),
        }
        write_result(output, result)
        raise RuntimeError("v150 source output hash mismatch")

    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join((str(competition / "kickmix"), str(competition / "verifiers")))
    verify = subprocess.run(
        [sys.executable, "-B", str(verifier), str(candidate), "--max-workers", "1"],
        cwd=competition,
        env=env,
        capture_output=True,
        text=True,
        timeout=7200,
    )
    (output / "verify.stdout.json").write_text(verify.stdout, encoding="utf-8")
    (output / "verify.stderr.log").write_text(verify.stderr, encoding="utf-8")
    try:
        verification = json.loads(verify.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("official verifier did not return JSON") from exc

    result = {
        "experiment": "exp-100",
        "status": "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS" if verify.returncode == 0 and verification.get("status") == "PASS" else "OFFICIAL_VERIFIER_FAILED",
        "source": {"dataset": SOURCE_DATASET, "archive_sha256": sha256_file(archive), "compiled_input_used": False, "internet_enabled": False},
        "candidate_sha256": candidate_sha,
        "official_verifier": verification,
        "comparison": None,
        "seconds": round(time.monotonic() - started, 2),
    }
    if verification.get("status") == "PASS":
        score = float(verification["score"])
        tie_gate = BASELINE_DQI_COST * (BASELINE_PROJECTION / LEADER_SCORE) ** 3
        result["comparison"] = {
            "leader_score_snapshot": LEADER_SCORE,
            "s001_projection_if_other_components_fixed": BASELINE_PROJECTION * (BASELINE_DQI_COST / score) ** (1 / 3),
            "dqi_score": score,
            "dqi_mean_toffolis": float(verification["toffoli_count"]),
            "dqi_qubits": int(verification["num_qubits"]),
            "repetition_factor": float(verification["repetition_factor"]),
            "dqi_cost_tie_gate": tie_gate,
            "dqi_cost_above_tie_gate_pct": (score / tie_gate - 1) * 100,
            "meets_tie_gate": score <= tie_gate,
        }
    write_result(output, result)
    if result["status"] != "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS":
        raise RuntimeError("official verifier failed")


if __name__ == "__main__":
    main()
