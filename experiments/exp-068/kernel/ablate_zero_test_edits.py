"""Rebuild DQI from pinned source, keep two published edits, and verify."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


DATASET_SLUG = "quantum-ai-32-85306-task-generators"
MANIFEST_SHA256 = "192853425ad64fd80ecc07aa904dc55b2adf53c7c3dff2cdce81babdb6eed9ce"
KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASE_DQI_SHA256 = "4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52"
OUT = Path("/kaggle/working/exp068")

# Retain the two published edits; omit the eight zero-test CCX rewrites.
EDITS = (
    (
        "evgendvorkin: CCZ to CZ",
        "X q163\nCCZ q103 q54 q163\nX q54",
        "X q163\nCZ q103 q54\nX q54",
    ),
    (
        "ozertuu: delete redundant conditional CCZ",
        "CX q896 q507\nCCZ q63 q507 q204 if b49140\nCX q896 q507",
        "CX q896 q507\nCX q896 q507",
    ),
)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def sanitized_env(python_paths: list[Path]) -> dict[str, str]:
    env = os.environ.copy()
    for key in tuple(env):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            marker in upper
            for marker in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            env.pop(key, None)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(path) for path in python_paths] + list(filter(None, [env.get("PYTHONPATH")]))
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    return env


def locate_one(root: Path, filename: str) -> Path:
    paths = [path for path in root.rglob(filename) if path.is_file()]
    if len(paths) != 1:
        raise RuntimeError(f"expected one {filename}, found {len(paths)}")
    return paths[0]


def rewrite_kmx(source: Path, destination: Path) -> dict[str, object]:
    replacements = {
        tuple(old.splitlines()): (label, tuple(new.splitlines()))
        for label, old, new in EDITS
    }
    hits = Counter()
    before = Counter()
    after = Counter()

    def tally(counter: Counter, line: str) -> None:
        if line.startswith("CCX "):
            counter["CCX"] += 1
        elif line.startswith("CCZ "):
            counter["CCZ"] += 1

    window: list[str] = []
    with source.open("r", encoding="ascii") as src, destination.open(
        "w", encoding="ascii", newline="\n"
    ) as dst:
        for raw in src:
            window.append(raw.rstrip("\r\n"))
            if len(window) < 3:
                continue
            match = replacements.get(tuple(window))
            if match is None:
                line = window.pop(0)
                tally(before, line)
                tally(after, line)
                dst.write(line + "\n")
                continue
            label, new_lines = match
            hits[label] += 1
            for line in window:
                tally(before, line)
            for line in new_lines:
                tally(after, line)
                dst.write(line + "\n")
            window.clear()
        for line in window:
            tally(before, line)
            tally(after, line)
            dst.write(line + "\n")

    missing = [label for label, _, _ in EDITS if hits[label] != 1]
    if missing:
        raise RuntimeError(f"each retained edit must match once: {missing}")
    return {
        "retained_edits": dict(hits),
        "omitted_zero_test_rewrites": 8,
        "static_toffoli_like_before": before["CCX"] + before["CCZ"],
        "static_toffoli_like_after": after["CCX"] + after["CCZ"],
    }


def run_verifier(command: list[str], cwd: Path, env: dict[str, str], output: Path) -> dict[str, object]:
    start = time.monotonic()
    with output.open("w", encoding="utf-8") as stdout:
        run = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=subprocess.STDOUT)
    seconds = time.monotonic() - start
    if run.returncode:
        raise RuntimeError(f"official verifier failed ({run.returncode}); inspect {output}")
    raw = output.read_text(encoding="utf-8")
    start_json = raw.find("{")
    if start_json < 0:
        raise RuntimeError(f"verifier produced no JSON; inspect {output}")
    result = json.loads(raw[start_json:])
    if result.get("status") != "PASS":
        raise RuntimeError(f"official DQI verifier did not PASS: {result}")
    return {"seconds": round(seconds, 2), "result": result}


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"refusing to reuse existing output path {OUT}")
    OUT.mkdir(parents=True)
    input_root = Path("/kaggle/input")
    dataset_roots = [
        input_root / "datasets" / "tonylica" / DATASET_SLUG,
        input_root / DATASET_SLUG,
    ]
    dataset = next((path for path in dataset_roots if (path / "generate.py").is_file()), None)
    if dataset is None:
        raise RuntimeError("could not locate the pinned Tony Li source dataset")

    manifest_path = dataset / "expected_sha256.json"
    if sha256(manifest_path) != MANIFEST_SHA256:
        raise RuntimeError("pinned source manifest hash mismatch")

    competition = locate_one(input_root, "verify_submission_dqi.py").parents[2]
    kickmix_dir = competition / "kickmix"
    if sha256(kickmix_dir / "kickmix.so") != KICKMIX_SHA256:
        raise RuntimeError("official Kickmix SDK hash changed")
    env = sanitized_env([kickmix_dir, competition / "verifiers"])

    temp_root = Path("/kaggle/temp")
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="exp068-", dir=temp_root) as temporary:
        base_dir = Path(temporary) / "base"
        build_log = OUT / "source-build.log"
        build_start = time.monotonic()
        with build_log.open("w", encoding="utf-8") as log:
            build = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(dataset / "generate.py"),
                    "dqi",
                    "--output",
                    str(base_dir),
                ],
                cwd=dataset,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        build_seconds = round(time.monotonic() - build_start, 2)
        if build.returncode:
            raise RuntimeError(f"source DQI build failed; inspect {build_log}")

        base_dqi = base_dir / "dqi.kmb"
        base_hash = sha256(base_dqi)
        if base_hash != BASE_DQI_SHA256:
            raise RuntimeError(f"source-built DQI hash mismatch: {base_hash}")

        sys.path.insert(0, str(kickmix_dir))
        import kickmix

        circuit = kickmix.Circuit.from_file(str(base_dqi), "kmb")
        base_kmx = Path(temporary) / "base.kmx"
        circuit.to_file(str(base_kmx), format="kmx")
        del circuit

        rewritten_kmx = Path(temporary) / "candidate.kmx"
        gate_counts = rewrite_kmx(base_kmx, rewritten_kmx)
        circuit = kickmix.Circuit.from_file(str(rewritten_kmx), "kmx")
        candidate = OUT / "dqi.kmb"
        circuit.to_file(str(candidate), format="kmb")
        candidate_hash = sha256(candidate)
        del circuit

        verifier = locate_one(input_root, "verify_submission_dqi.py")
        dqi_result = run_verifier(
            [sys.executable, "-B", str(verifier), str(candidate), "--max-workers", "1"],
            competition,
            env,
            OUT / "verify-dqi.log",
        )

    result = {
        "experiment": "exp-068-dqi-zero-test-ablation",
        "status": "PASS",
        "source": {
            "dataset": f"tonylica/{DATASET_SLUG}/2",
            "manifest_sha256": MANIFEST_SHA256,
            "base_dqi_sha256": BASE_DQI_SHA256,
            "official_kickmix_sha256": KICKMIX_SHA256,
        },
        "build_seconds": build_seconds,
        "candidate_dqi_sha256": candidate_hash,
        "gate_counts": gate_counts,
        "dqi_verifier": dqi_result,
        "submission": "NOT_SUBMITTED",
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
