"""Build the pinned DQI source and measure it with the official verifier."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import time
import zipfile


SOURCE_BUNDLE_B85 = ""
SOURCE_BUNDLE_SHA256 = ""
EXPECTED_CIRCUIT_SHA256 = "b3354f60e459dcebe67910363e96498f8bb0aa7f699bc016ef962015c3732fd6"
EXPECTED_MANIFEST_SHA256 = ""
EXPECTED_VERIFIER_SHA256 = "f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65"
EXPECTED_KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASELINE_PROJECTION = 31.798180509655666
BASELINE_DQI_COST = 336559961203.1761
BASELINE_DQI_MEAN_T = 356677.4941796875
BASELINE_DQI_Q = 890
LEADER_SCORE = 34.65589


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unpack_source() -> Path:
    archive_bytes = base64.b85decode(SOURCE_BUNDLE_B85.encode("ascii"))
    if hashlib.sha256(archive_bytes).hexdigest() != SOURCE_BUNDLE_SHA256:
        raise RuntimeError("embedded source bundle hash mismatch")
    source_root = Path("/kaggle/temp/exp087-source")
    if source_root.exists():
        raise RuntimeError(f"refusing to reuse source path: {source_root}")
    source_root.mkdir(parents=True)
    total_bytes = 0
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for info in archive.infolist():
            member = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if member.is_absolute() or ".." in member.parts or "\\" in info.filename:
                raise RuntimeError(f"unsafe source archive member: {info.filename}")
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"symlink in source archive: {info.filename}")
            total_bytes += info.file_size
            if total_bytes > 20_000_000:
                raise RuntimeError("source archive exceeds the size limit")
            target = source_root.joinpath(*member.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as reader, target.open("wb") as writer:
                shutil.copyfileobj(reader, writer)
    if sha256(source_root / "MANIFEST.json") != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("source manifest hash mismatch")
    return source_root


def locate_competition() -> tuple[Path, Path]:
    matches = [p for p in Path("/kaggle/input").rglob("verify_submission_dqi.py")
               if p.parent.name == "dqi"]
    if len(matches) != 1:
        raise RuntimeError(f"expected one official DQI verifier, found {len(matches)}")
    verifier = matches[0]
    root = verifier.parent.parent.parent
    kickmix = root / "kickmix" / "kickmix.so"
    if not kickmix.is_file():
        raise RuntimeError(f"official Kickmix extension missing: {kickmix}")
    if sha256(verifier) != EXPECTED_VERIFIER_SHA256:
        raise RuntimeError("official verifier hash differs from the pinned version")
    if sha256(kickmix) != EXPECTED_KICKMIX_SHA256:
        raise RuntimeError("official Kickmix hash differs from the pinned version")
    return root, verifier


def sanitized_env(kickmix_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    for key in tuple(env):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            marker in upper for marker in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            env.pop(key, None)
    env["PYTHONPATH"] = str(kickmix_dir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def main() -> None:
    started = time.monotonic()
    source_root = unpack_source()
    competition_root, verifier = locate_competition()
    out = Path("/kaggle/working/exp087")
    if out.exists():
        raise RuntimeError(f"refusing to reuse output path: {out}")
    out.mkdir(parents=True)
    shutil.copyfile(source_root / "LICENSE", out / "UPSTREAM-LICENSE.txt")
    shutil.copyfile(source_root / "NOTICE", out / "UPSTREAM-NOTICE.txt")
    env = sanitized_env(competition_root / "kickmix")

    candidate = out / "dqi.kmb"
    with (out / "build.log").open("w", encoding="utf-8") as log:
        built = subprocess.run(
            [sys.executable, "-B", str(source_root / "generate.py"), str(candidate)],
            cwd=source_root, env=env, stdout=log, stderr=subprocess.STDOUT,
        )
    if built.returncode:
        raise RuntimeError(f"source build failed with exit code {built.returncode}")
    build = json.loads(candidate.with_suffix(".build.json").read_text(encoding="utf-8"))
    candidate_sha = sha256(candidate)
    if candidate_sha != EXPECTED_CIRCUIT_SHA256 or not build.get("matches_upstream_stated"):
        raise RuntimeError(f"source build did not reproduce the pinned output: {candidate_sha}")

    verify_command = [sys.executable, "-B", str(verifier), str(candidate), "--max-workers", "1"]
    with (out / "verify.stdout.json").open("w", encoding="utf-8") as stdout, \
         (out / "verify.stderr.log").open("w", encoding="utf-8") as stderr:
        verified = subprocess.run(verify_command, cwd=competition_root, env=env, stdout=stdout, stderr=stderr)
    verification = json.loads((out / "verify.stdout.json").read_text(encoding="utf-8"))
    if verified.returncode or verification.get("status") != "PASS":
        raise RuntimeError(f"official DQI verifier failed: {verification}")
    if verification.get("circuit_sha256") != EXPECTED_CIRCUIT_SHA256:
        raise RuntimeError("official verifier reported a different circuit hash")

    mean_t = float(verification["toffoli_count"])
    qubits = int(verification["num_qubits"])
    dqi_cost = float(verification["score"])
    dqi_cost_gate = BASELINE_DQI_COST * (BASELINE_PROJECTION / LEADER_SCORE) ** 3
    repetition_factor = float(verification["repetition_factor"])
    projected_score = BASELINE_PROJECTION * (BASELINE_DQI_COST / dqi_cost) ** (1.0 / 3.0)
    tie_gate_at_q = dqi_cost_gate / (repetition_factor * qubits**2)
    result = {
        "experiment": "exp-087",
        "status": "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS",
        "source": {
            "origin": "somejoint/quantum-circuits-22-77-local-gm-889-qubit-dqi, version 14",
            "license": "Apache-2.0",
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "source_bundle_sha256": SOURCE_BUNDLE_SHA256,
            "upstream_design_lineage_caveat": "See bundled NOTICE; lineage passes through a repository with no license.",
            "public_circuit_binary_used_as_build_input": False,
            "internet_enabled": False,
        },
        "build": build,
        "candidate_sha256": candidate_sha,
        "official_verifier": verification,
        "comparison": {
            "leader_score_snapshot": LEADER_SCORE,
            "s001_projection_if_other_components_fixed": projected_score,
            "dqi_mean_toffolis": mean_t,
            "dqi_cost": dqi_cost,
            "dqi_cost_tie_gate": dqi_cost_gate,
            "repetition_factor": repetition_factor,
            "mean_tie_gate_at_measured_q": tie_gate_at_q,
            "meets_tie_gate": dqi_cost <= dqi_cost_gate,
        },
        "build_and_verify_seconds": round(time.monotonic() - started, 2),
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
