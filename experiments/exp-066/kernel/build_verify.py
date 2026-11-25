"""Rebuild a licensed source portfolio, rewrite its DQI gates, and verify all tasks."""

from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile


DATASET_SLUG = "quantum-ai-32-85306-task-generators"
DATASET_FINGERPRINT = "50be321af83901e46476b55c7b1faedf60510f971abc495c02aa41f8c9b87e42"
MANIFEST_SHA256 = "192853425ad64fd80ecc07aa904dc55b2adf53c7c3dff2cdce81babdb6eed9ce"
KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASE_DQI_SHA256 = "4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52"
REWRITTEN_DQI_SHA256 = "6f78ecdd636051d4d2dd8f24aaece1d454eb220aaf0df2c1d64c3d96fe22081d"
OUT = Path("/kaggle/working/exp066")


# The ten exact rewrites published by areebbb/qai-the-26-toffoli-cut-lb-33-21010.
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
    (
        "zero-test position 17",
        "X q337\nCCX q7 q337 q83\nX q337",
        "X q337\nCX q7 q83\nX q337",
    ),
    (
        "zero-test position 18",
        "X q692\nCCX q83 q692 q26\nX q692",
        "X q692\nCX q83 q26\nX q692",
    ),
    (
        "zero-test position 19",
        "X q471\nCCX q26 q471 q219\nX q471",
        "X q471\nCX q26 q219\nX q471",
    ),
    (
        "zero-test position 20",
        "X q254\nCCX q219 q254 q189\nX q254",
        "X q254\nCX q219 q189\nX q254",
    ),
    (
        "zero-test position 21",
        "X q355\nCCX q189 q355 q179\nX q355",
        "X q355\nCX q189 q179\nX q355",
    ),
    (
        "zero-test position 22",
        "X q483\nCCX q179 q483 q85\nX q483",
        "X q483\nCX q179 q85\nX q483",
    ),
    (
        "zero-test position 23",
        "X q300\nCCX q85 q300 q188\nX q300",
        "X q300\nCX q85 q188\nX q300",
    ),
    (
        "zero-test position 24",
        "X q585\nCCX q188 q585 q78\nX q585",
        "X q585\nCX q188 q78\nX q585",
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


def dataset_fingerprint(root: Path) -> tuple[str, int]:
    rows = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(
            part.startswith(".") or part == "__pycache__" for part in relative.parts
        ):
            continue
        rows.append((relative.as_posix(), sha256(path)))
    payload = "".join(f"{name}\t{digest}\n" for name, digest in rows).encode()
    return hashlib.sha256(payload).hexdigest(), len(rows)


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
        raise RuntimeError(f"each rewrite must match exactly once; missing/duplicate: {missing}")
    return {
        "rewrites": dict(hits),
        "static_toffoli_like_before": before["CCX"] + before["CCZ"],
        "static_toffoli_like_after": after["CCX"] + after["CCZ"],
        "static_CCX_before": before["CCX"],
        "static_CCX_after": after["CCX"],
        "static_CCZ_before": before["CCZ"],
        "static_CCZ_after": after["CCZ"],
    }


def run_verifier(command: list[str], cwd: Path, env: dict[str, str], output: Path) -> dict[str, object]:
    start = time.monotonic()
    with output.open("w", encoding="utf-8") as stdout:
        run = subprocess.run(command, cwd=cwd, env=env, stdout=stdout, stderr=subprocess.STDOUT)
    seconds = time.monotonic() - start
    if run.returncode:
        raise RuntimeError(f"verifier failed ({run.returncode}); inspect {output}")
    raw = output.read_text(encoding="utf-8")
    start_json = raw.find("{")
    if start_json < 0:
        raise RuntimeError(f"verifier produced no JSON; inspect {output}")
    result = json.loads(raw[start_json:])
    if result.get("status") != "PASS":
        raise RuntimeError(f"official verifier did not PASS: {result}")
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
        raise RuntimeError("could not locate the pinned Tony Li generator dataset")

    fingerprint, file_count = dataset_fingerprint(dataset)
    manifest_path = dataset / "expected_sha256.json"
    if fingerprint != DATASET_FINGERPRINT or sha256(manifest_path) != MANIFEST_SHA256:
        raise RuntimeError("the mounted generator dataset differs from the pinned version")

    competition = locate_one(input_root, "verify_submission_dqi.py").parents[2]
    kickmix_dir = competition / "kickmix"
    kickmix_file = kickmix_dir / "kickmix.so"
    if sha256(kickmix_file) != KICKMIX_SHA256:
        raise RuntimeError("official competition Kickmix SDK hash changed")
    env = sanitized_env([kickmix_dir, competition / "verifiers"])

    with tempfile.TemporaryDirectory(prefix="exp066-", dir="/kaggle/temp") as temporary:
        temp = Path(temporary)
        base_output = temp / "base"
        base_output.parent.mkdir(parents=True, exist_ok=True)
        build_log = OUT / "source-build.log"
        build_start = time.monotonic()
        with build_log.open("w", encoding="utf-8") as log:
            build = subprocess.run(
                [sys.executable, "-B", str(dataset / "generate.py"), "all", "--output", str(base_output)],
                cwd=dataset,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        build_seconds = time.monotonic() - build_start
        if build.returncode:
            raise RuntimeError(f"source portfolio build failed ({build.returncode}); inspect {build_log}")

        base_dqi = base_output / "dqi.kmb"
        if sha256(base_dqi) != BASE_DQI_SHA256:
            raise RuntimeError("source-built base DQI hash differs from the pinned release")

        sys.path.insert(0, str(kickmix_dir))
        import kickmix

        circuit = kickmix.Circuit.from_file(str(base_dqi), "kmb")
        base_kmx = temp / "base.kmx"
        circuit.to_file(str(base_kmx), format="kmx")
        del circuit

        rewritten_kmx = temp / "rewritten.kmx"
        gate_counts = rewrite_kmx(base_kmx, rewritten_kmx)
        circuit = kickmix.Circuit.from_file(str(rewritten_kmx), "kmx")
        rewritten_dqi = OUT / "dqi.kmb"
        circuit.to_file(str(rewritten_dqi), format="kmb")
        qubits = int(circuit.num_qubits)
        del circuit
        rewritten_hash = sha256(rewritten_dqi)
        if rewritten_hash != REWRITTEN_DQI_SHA256:
            raise RuntimeError(f"rewritten DQI hash mismatch: {rewritten_hash}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["dqi.kmb"] = rewritten_hash
        archive = OUT / "submission.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
            for name in sorted(manifest):
                path = rewritten_dqi if name == "dqi.kmb" else base_output / name
                if sha256(path) != manifest[name]:
                    raise RuntimeError(f"candidate member hash mismatch: {name}")
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                with path.open("rb") as source, output.open(info, "w") as target:
                    shutil.copyfileobj(source, target, 1 << 20)
        with zipfile.ZipFile(archive) as check:
            if len(check.namelist()) != 18 or set(check.namelist()) != set(manifest):
                raise RuntimeError("candidate archive member set is invalid")

        invsqrt_verifier = locate_one(input_root, "verify_submission_invsqrt.py")
        dqi_verifier = locate_one(input_root, "verify_submission_dqi.py")
        chemistry_verifiers = [
            path for path in input_root.rglob("verify.py")
            if path.parent.name == "dfthcsos"
        ]
        if len(chemistry_verifiers) != 1:
            raise RuntimeError(
                f"expected one dfthcsos verifier, found {len(chemistry_verifiers)}"
            )
        chemistry_verifier = chemistry_verifiers[0]

        invsqrt_result = run_verifier(
            [sys.executable, "-B", str(invsqrt_verifier), str(base_output / "invsqrt.kmb")],
            competition,
            env,
            OUT / "verify-invsqrt.log",
        )
        dqi_result = run_verifier(
            [sys.executable, "-B", str(dqi_verifier), str(rewritten_dqi), "--max-workers", "1"],
            competition,
            env,
            OUT / "verify-dqi.log",
        )

        spec = importlib.util.spec_from_file_location("official_dfthcsos_verify", chemistry_verifier)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load official dfthcsos verifier")
        official_chemistry = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = official_chemistry
        spec.loader.exec_module(official_chemistry)
        chemistry_start = time.monotonic()
        with (OUT / "verify-chemistry.log").open("w", encoding="utf-8") as log:
            result = official_chemistry.verify(str(base_output / "dfthcsos"))
            log.write(json.dumps(result, indent=2, default=lambda value: value.item() if hasattr(value, "item") else str(value)))
        chemistry_result = {"seconds": round(time.monotonic() - chemistry_start, 2), "result": result}
        if result.get("status") != "PASS":
            raise RuntimeError(f"official chemistry verifier did not PASS: {result}")

        result = {
            "experiment": "exp-066-source-built-dqi-gate-rewrites",
            "status": "PASS",
            "source": {
                "dataset": "tonylica/quantum-ai-32-85306-task-generators",
                "license": "Apache-2.0",
                "files": file_count,
                "fingerprint": fingerprint,
                "manifest_sha256": sha256(manifest_path),
                "official_kickmix_sha256": sha256(kickmix_file),
            },
            "build_seconds": round(build_seconds, 2),
            "base_dqi_sha256": BASE_DQI_SHA256,
            "rewritten_dqi_sha256": rewritten_hash,
            "rewritten_dqi_qubits": qubits,
            "gate_counts": gate_counts,
            "archive_sha256": sha256(archive),
            "archive_bytes": archive.stat().st_size,
            "member_sha256": manifest,
            "verifiers": {
                "invsqrt": invsqrt_result,
                "dqi": dqi_result,
                "dfthcsos": chemistry_result,
            },
            "submission": "NOT_SUBMITTED",
        }
        (OUT / "result.json").write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, default=str), flush=True)


if __name__ == "__main__":
    main()
