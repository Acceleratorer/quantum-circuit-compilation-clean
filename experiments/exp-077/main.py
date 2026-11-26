"""Build and verify the source-owned DQI rank-99 phase-product experiment."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
import zipfile


SOURCE_BUNDLE_B85 = "__SOURCE_BUNDLE_B85__"
KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASELINE_DQI_SHA256 = "4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52"
BASELINE_DQI_SCORE = 305041647011.3978
RANK1_TIE_DQI_SCORE = 268964550804.47
OUT = Path("/kaggle/working/exp077")


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def competition_root() -> Path:
    input_root = Path("/kaggle/input")
    candidates = (
        input_root / "competitions" / "google-verifiable-quantum-circuit-compilation",
        input_root / "google-verifiable-quantum-circuit-compilation",
    )
    for path in candidates:
        if (path / "kickmix" / "kickmix.so").is_file() and (path / "verifiers" / "dqi").is_dir():
            return path
    raise RuntimeError("Attached competition SDK and DQI verifier were not found")


def unpack_source(destination: Path) -> Path:
    if destination.exists():
        raise RuntimeError(f"Refusing to reuse source path: {destination}")
    destination.mkdir(parents=True)
    archive_bytes = base64.b85decode(SOURCE_BUNDLE_B85)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for item in archive.infolist():
            relative = PurePosixPath(item.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe source archive member: {item.filename}")
            target = destination.joinpath(*relative.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(item))
    return destination / "dqi"


def verifier_result(verifier: Path, circuit: Path, log: Path, seed: int | None, env: dict[str, str]) -> dict:
    command = [sys.executable, "-B", str(verifier), str(circuit), "--max-workers", "4"]
    if seed is not None:
        command.extend(["--seed", str(seed)])
    with log.open("w", encoding="utf-8") as stream:
        run = subprocess.run(command, cwd=verifier.parent.parent, env=env, stdout=stream, stderr=subprocess.STDOUT)
    output = log.read_text(encoding="utf-8")
    if run.returncode:
        raise RuntimeError(f"DQI verifier failed ({run.returncode}); inspect {log}")
    decoder = json.JSONDecoder()
    payload = None
    for index, char in enumerate(output):
        if char == "{":
            try:
                item, _ = decoder.raw_decode(output[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and "status" in item:
                payload = item
    if payload is None or payload.get("status") != "PASS":
        raise RuntimeError(f"DQI verifier did not PASS; inspect {log}")
    return payload


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"Refusing to reuse output path: {OUT}")
    OUT.mkdir(parents=True)
    competition = competition_root()
    kickmix_dir = competition / "kickmix"
    if sha256_file(kickmix_dir / "kickmix.so") != KICKMIX_SHA256:
        raise RuntimeError("Competition Kickmix SDK hash differs from the pinned release")
    source_dir = unpack_source(OUT / "source")
    sys.path[:0] = [str(source_dir), str(kickmix_dir), str(competition / "verifiers")]
    import kickmix  # noqa: F401

    import generate as dqi_generator

    build_started = time.monotonic()
    circuit = OUT / "dqi.kmb"
    build = dqi_generator.build(circuit, phase_product_rank99=True)
    build_seconds = round(time.monotonic() - build_started, 2)
    if build["sha256"] == BASELINE_DQI_SHA256:
        raise RuntimeError("Rank-99 phase path unexpectedly reproduced the baseline bytes")

    verifier = competition / "verifiers" / "dqi" / "verify_submission_dqi.py"
    verifier_env = os.environ.copy()
    for key in tuple(verifier_env):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            marker in upper
            for marker in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            verifier_env.pop(key, None)
    verifier_env["PYTHONPATH"] = os.pathsep.join(
        [str(kickmix_dir), str(competition / "verifiers")]
        + list(filter(None, [verifier_env.get("PYTHONPATH")]))
    )
    verifier_env["PYTHONDONTWRITEBYTECODE"] = "1"
    verifier_env["OMP_NUM_THREADS"] = "1"
    verifier_env["OPENBLAS_NUM_THREADS"] = "1"
    default = verifier_result(verifier, circuit, OUT / "verify-default.log", None, verifier_env)
    seeded = verifier_result(verifier, circuit, OUT / "verify-seed-20261126.log", 20261126, verifier_env)
    if default["num_qubits"] != seeded["num_qubits"]:
        raise RuntimeError("Verifier seeds changed the circuit width")
    for name, result in (("default", default), ("seeded", seeded)):
        if result["value_errors"] or result["phase_errors"]:
            raise RuntimeError(f"Verifier seed {name} observed DQI errors")

    source_score = default["score"]
    source_geometric = (
        (2076774.233715282 / 61696.23146663024)
        * (24439463583672.93 / source_score)
        * (3355599588.3155375 / 249853852.96142676)
    ) ** (1 / 3)
    receipt = {
        "experiment": "exp-077",
        "status": "PASS",
        "submission_status": "NOT_SUBMITTED",
        "source": {
            "generator": "repo src/dqi source build",
            "phase_product": "99-term exact GF(2^24) tensor; baseline is five GF(2^12) phase products",
            "compiled_input_circuits_read": 0,
            "build_seconds": build_seconds,
            "phase_product_profile": build["phase_product_profile"],
            "build": build,
            "sha256": sha256_file(circuit),
        },
        "verifiers": {"default_hash_seed": default, "explicit_seed_20261126": seeded},
        "comparison": {
            "baseline_dqi_score": BASELINE_DQI_SCORE,
            "candidate_dqi_score": source_score,
            "dqi_improvement_percent": 100 * (1 - source_score / BASELINE_DQI_SCORE),
            "rank1_tie_dqi_score_gate": RANK1_TIE_DQI_SCORE,
            "rank1_gate_met": source_score < RANK1_TIE_DQI_SCORE,
            "portfolio_geometric_score_with_exp074_other_members": source_geometric,
            "is_public_score_projection": False,
        },
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
