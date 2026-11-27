"""Rebuild the QV2 DQI generator source and run Google's official verifier."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import time


EXPECTED_SOURCE_FILES = {}
SOURCE_MANIFEST_SHA256 = ""
UPSTREAM_GENERATORS_MANIFEST_SHA256 = "623c1127bbfe18083ebab46ad2338444451071ded5c4ed319f64f07f1d265a0a"
LOCAL_DATASET_SNAPSHOT_SHA256 = "9fe082e0d22e3b95b802b0c0ba548c6798ebd869cff503446af2fb82ea11148e"
SOURCE_DATASET = "mliston/vqcc-milestone-generators-32-30740"
EXPECTED_CIRCUIT_SHA256 = "3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3"
EXPECTED_VERIFIER_SHA256 = "f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65"
EXPECTED_KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASELINE_PROJECTION = 31.798180509655666
BASELINE_DQI_COST = 336559961203.1761
LEADER_SCORE = 34.65589


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unpack_source(source_root: Path, dataset_root: Path) -> dict:
    manifest_bytes = json.dumps(EXPECTED_SOURCE_FILES, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(manifest_bytes).hexdigest() != SOURCE_MANIFEST_SHA256:
        raise RuntimeError("embedded source manifest hash mismatch")
    if source_root.exists():
        raise RuntimeError(f"refusing to reuse source path: {source_root}")
    source_root.mkdir(parents=True)

    if sha256_file(dataset_root / "generators/MANIFEST.sha256") != UPSTREAM_GENERATORS_MANIFEST_SHA256:
        raise RuntimeError("upstream generator manifest hash mismatch")
    root_docs = {
        "CREDITS.md": "generators/CREDITS.md",
        "DEPENDENCIES.md": "generators/DEPENDENCIES.md",
        "LICENSE": "generators/LICENSE",
        "NOTICE": "generators/NOTICE",
        "KIT_README.md": "generators/README.md",
    }
    dataset_root = dataset_root.resolve()
    for name, digest in EXPECTED_SOURCE_FILES.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name:
            raise RuntimeError(f"unsafe pinned source path: {name}")
        if name.startswith("kit/"):
            source_name = "generators/dqi/" + name.removeprefix("kit/")
        else:
            source_name = root_docs[name]
        source = dataset_root.joinpath(*PurePosixPath(source_name).parts)
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(dataset_root):
            raise RuntimeError(f"missing or unsafe Kaggle source file: {source_name}")
        if source.stat().st_size > 20_000_000 or PurePosixPath(source_name).suffix.lower() in {".kmb", ".kmx", ".npz"}:
            raise RuntimeError(f"unexpected compiled or oversized source member: {source_name}")
        if sha256_file(source) != digest:
            raise RuntimeError(f"source file hash mismatch: {source_name}")
        target = source_root.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return {
        "dataset": SOURCE_DATASET,
        "local_dataset_snapshot_sha256": LOCAL_DATASET_SNAPSHOT_SHA256,
        "upstream_manifest_sha256": UPSTREAM_GENERATORS_MANIFEST_SHA256,
        "manifest_sha256": SOURCE_MANIFEST_SHA256,
        "files": EXPECTED_SOURCE_FILES,
    }


def write_run_result(output: Path, result: dict) -> None:
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


def main() -> None:
    started = time.monotonic()
    output = Path("/kaggle/working/exp089")
    if output.exists():
        raise RuntimeError(f"refusing to reuse result path: {output}")
    output.mkdir(parents=True)

    competition = Path("/kaggle/input/google-verifiable-quantum-circuit-compilation")
    dataset_root = Path("/kaggle/input/vqcc-milestone-generators-32-30740")
    verifier = competition / "verifiers/dqi/verify_submission_dqi.py"
    kickmix = competition / "kickmix/kickmix.so"
    if not verifier.is_file() or not kickmix.is_file():
        raise RuntimeError(f"official competition inputs are missing under {competition}")
    if sha256_file(verifier) != EXPECTED_VERIFIER_SHA256:
        raise RuntimeError("official DQI verifier hash mismatch")
    if sha256_file(kickmix) != EXPECTED_KICKMIX_SHA256:
        raise RuntimeError("official kickmix hash mismatch")

    run_root = Path(tempfile.mkdtemp(prefix="exp089-qv2-"))
    source_root = run_root / "source"
    manifest = unpack_source(source_root, dataset_root)
    build_dir = run_root / "build"
    rebuild = source_root / "kit/rebuild.py"
    build = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(rebuild),
            "--official",
            str(competition),
            "--python",
            sys.executable,
            "--out",
            str(build_dir),
            "--cpu",
            "0",
            "--no-sandbox",
        ],
        cwd=source_root,
        capture_output=True,
        text=True,
        timeout=7200,
    )
    (output / "build.stdout.log").write_text(build.stdout, encoding="utf-8")
    (output / "build.stderr.log").write_text(build.stderr, encoding="utf-8")
    if build.returncode:
        result = {
            "experiment": "exp-089",
            "status": "SOURCE_BUILD_FAILED",
            "exit_code": build.returncode,
            "build_stdout_tail": build.stdout[-2000:],
            "build_stderr_tail": build.stderr[-2000:],
        }
        write_run_result(output, result)
        raise RuntimeError("QV2 DQI source build failed")

    build_record = json.loads((build_dir / "rebuild.json").read_text(encoding="utf-8"))
    candidate = build_dir / "build/dqi.kmb"
    candidate_sha = sha256_file(candidate)
    if candidate_sha != EXPECTED_CIRCUIT_SHA256 or not build_record.get("match"):
        result = {
            "experiment": "exp-089",
            "status": "SOURCE_OUTPUT_HASH_MISMATCH",
            "candidate_sha256": candidate_sha,
            "expected_sha256": EXPECTED_CIRCUIT_SHA256,
            "build": build_record,
        }
        write_run_result(output, result)
        raise RuntimeError("QV2 DQI source build did not reproduce the pinned output")

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
        raise RuntimeError("official DQI verifier did not return JSON") from exc

    result = {
        "experiment": "exp-089",
        "status": "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS"
        if verify.returncode == 0 and verification.get("status") == "PASS"
        else "OFFICIAL_VERIFIER_FAILED",
        "source": {
            "origin": "mliston/vqcc-milestone-generators-32-30740, generators/dqi/",
            "license": "Apache-2.0",
            "manifest_sha256": manifest["manifest_sha256"],
            "upstream_manifest_sha256": manifest["upstream_manifest_sha256"],
            "local_dataset_snapshot_sha256": manifest["local_dataset_snapshot_sha256"],
            "manifest_files": len(manifest["files"]),
            "public_circuit_binary_used_as_build_input": False,
            "internet_enabled": False,
            "multiplication_table_provenance": "J_A and J_B were read from Syed Asad Ali's compiled decoder; see src/dqi/qv2_m4/UPSTREAM.md",
        },
        "build": build_record,
        "candidate_sha256": candidate_sha,
        "official_verifier": verification,
        "comparison": None,
        "build_and_verify_seconds": round(time.monotonic() - started, 2),
    }
    if verification.get("status") == "PASS":
        score = float(verification["score"])
        qubits = int(verification["num_qubits"])
        mean_t = float(verification["toffoli_count"])
        repetition_factor = float(verification["repetition_factor"])
        dqi_cost_gate = BASELINE_DQI_COST * (BASELINE_PROJECTION / LEADER_SCORE) ** 3
        result["comparison"] = {
            "leader_score_snapshot": LEADER_SCORE,
            "s001_projection_if_other_components_fixed": BASELINE_PROJECTION
            * (BASELINE_DQI_COST / score) ** (1.0 / 3.0),
            "dqi_mean_toffolis": mean_t,
            "dqi_qubits": qubits,
            "repetition_factor": repetition_factor,
            "dqi_score": score,
            "dqi_cost_tie_gate": dqi_cost_gate,
            "dqi_cost_above_tie_gate_pct": (score / dqi_cost_gate - 1.0) * 100,
            "meets_tie_gate": score <= dqi_cost_gate,
        }

    shutil.copyfile(candidate, output / "dqi.kmb")
    write_run_result(output, result)
    if verify.returncode or verification.get("status") != "PASS":
        raise RuntimeError("official DQI verifier failed")


if __name__ == "__main__":
    main()
