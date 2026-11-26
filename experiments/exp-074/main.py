"""Source-build and verify the exp-074 portfolio in Kaggle's Linux runtime."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time
import zipfile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "module"))
from build_chemistry import build_chemistry


DATASET_SLUG = "quantum-ai-32-85306-task-generators"
DATASET_FINGERPRINT = "50be321af83901e46476b55c7b1faedf60510f971abc495c02aa41f8c9b87e42"
MANIFEST_SHA256 = "192853425ad64fd80ecc07aa904dc55b2adf53c7c3dff2cdce81babdb6eed9ce"
KICKMIX_SHA256 = "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e"
BASE_DQI_SHA256 = "4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52"
INVSQRT_SHA256 = "68eb8c13ebc75c5e443ed5a8c6357c2c77e6676c499ed1324108bf025faf1489"
TABLE_SHA256 = "ec85d969811623b5b4c7e3fff26fef2151bafedaa9a4741cb978e56ff34fbba1"
REFERENCES = {
    "invsqrt": 2076774.233715282,
    "dqi": 24439463583672.93,
    "dfthcsos": 3355599588.3155375,
}
OUT = Path("/kaggle/working/exp074")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dataset_fingerprint(root: Path) -> tuple[str, int]:
    hashes = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(
            part.startswith(".") or part == "__pycache__" for part in relative.parts
        ):
            continue
        hashes[relative.as_posix()] = file_sha256(path)
    payload = "".join(f"{name}\t{digest}\n" for name, digest in sorted(hashes.items()))
    return sha256(payload.encode("utf-8")), len(hashes)


def locate_dataset(input_root: Path) -> Path:
    candidates = (
        input_root / "datasets" / "tonylica" / DATASET_SLUG,
        input_root / DATASET_SLUG,
    )
    for candidate in candidates:
        if (candidate / "generate.py").is_file():
            return candidate
    matches = [path.parent for path in input_root.rglob("generate.py") if path.parent.name == DATASET_SLUG]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one attached source dataset; found {len(matches)}")
    return matches[0]


def find_competition(input_root: Path) -> Path:
    candidates = (
        input_root / "competitions" / "google-verifiable-quantum-circuit-compilation",
        input_root / "google-verifiable-quantum-circuit-compilation",
    )
    for candidate in candidates:
        if (candidate / "verifiers").is_dir() and (candidate / "kickmix" / "kickmix.so").is_file():
            return candidate
    matches = [
        path.parent
        for path in input_root.rglob("verify_submission_dqi.py")
        if path.parent.name == "dqi" and (path.parents[2] / "kickmix" / "kickmix.so").is_file()
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one competition SDK; found {len(matches)}")
    return matches[0]


def extract_table(input_root: Path, competition: Path, destination: Path) -> str:
    """Read only the pinned raw parameter NPZ; never read a compiled input circuit."""
    found: list[bytes] = []
    for path in sorted(input_root.rglob("*")):
        if not path.is_file() or competition in path.parents:
            continue
        if path.name == "submission.npz":
            data = path.read_bytes()
            if sha256(data) == TABLE_SHA256:
                found.append(data)
        elif path.suffix.lower() in (".zip", ".pack"):
            try:
                with zipfile.ZipFile(path) as archive:
                    for member in archive.namelist():
                        if PurePosixPath(member).name != "submission.npz":
                            continue
                        data = archive.read(member)
                        if sha256(data) == TABLE_SHA256:
                            found.append(data)
            except zipfile.BadZipFile:
                continue
    if not found:
        raise RuntimeError("The pinned raw Maoxin parameter table was not attached")
    if any(item != found[0] for item in found[1:]):
        raise RuntimeError("Multiple different copies of the pinned parameter table were found")
    destination.write_bytes(found[0])
    return sha256(found[0])


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


def run_verifier(args: list[str], cwd: Path, env: dict[str, str], output: Path) -> dict:
    started = time.monotonic()
    with output.open("w", encoding="utf-8") as stream:
        run = subprocess.run(
            [sys.executable, "-B", *args],
            cwd=cwd,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    if run.returncode:
        raise RuntimeError(f"Verifier failed ({run.returncode}); inspect {output}")
    text = output.read_text(encoding="utf-8")
    payload = None
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            item, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and "status" in item:
            payload = item
    if payload is None or payload.get("status") != "PASS":
        raise RuntimeError(f"Official verifier did not PASS; inspect {output}")
    return {"seconds": round(time.monotonic() - started, 2), "result": payload}


def write_archive(submission_dir: Path, archive_path: Path) -> dict[str, str]:
    members = [
        "invsqrt.kmb",
        "dqi.kmb",
        *[f"dfthcsos/angle_k_{index}.kmb" for index in range(15)],
        "dfthcsos/submission.npz",
    ]
    hashes = {}
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in members:
            path = submission_dir / Path(name)
            if not path.is_file():
                raise RuntimeError(f"Submission member missing: {name}")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with path.open("rb") as source, archive.open(info, "w") as target:
                shutil.copyfileobj(source, target, 1 << 20)
            hashes[name] = file_sha256(path)
    with zipfile.ZipFile(archive_path) as archive:
        if set(archive.namelist()) != set(members) or len(archive.namelist()) != 18:
            raise RuntimeError("Submission archive has an invalid member set")
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"Submission archive CRC failed: {bad_member}")
        for name, digest in hashes.items():
            if sha256(archive.read(name)) != digest:
                raise RuntimeError(f"Submission archive member hash mismatch: {name}")
    return hashes


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"Refusing to reuse existing output path: {OUT}")
    OUT.mkdir(parents=True)
    input_root = Path("/kaggle/input")
    dataset = locate_dataset(input_root)
    competition = find_competition(input_root)
    kickmix_dir = competition / "kickmix"
    verifier_dir = competition / "verifiers"
    kickmix_path = kickmix_dir / "kickmix.so"
    if file_sha256(kickmix_path) != KICKMIX_SHA256:
        raise RuntimeError("Competition Kickmix SDK hash differs from the pinned release")
    fingerprint, file_count = dataset_fingerprint(dataset)
    manifest = dataset / "expected_sha256.json"
    if fingerprint != DATASET_FINGERPRINT or file_sha256(manifest) != MANIFEST_SHA256:
        raise RuntimeError("Attached Tony Li source dataset does not match the pinned version")

    env = sanitized_env([kickmix_dir, verifier_dir])
    sys.path[:0] = [str(kickmix_dir), str(verifier_dir)]
    import kickmix

    source_output = OUT / "source-build"
    build_started = time.monotonic()
    with (OUT / "source-build.log").open("w", encoding="utf-8") as stream:
        run = subprocess.run(
            [sys.executable, "-B", str(dataset / "generate.py"), "all", "--output", str(source_output)],
            cwd=dataset,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    if run.returncode:
        raise RuntimeError("Pinned source generator failed; inspect source-build.log")
    build_seconds = round(time.monotonic() - build_started, 2)
    base_dqi = source_output / "dqi.kmb"
    base_invsqrt = source_output / "invsqrt.kmb"
    if file_sha256(base_dqi) != BASE_DQI_SHA256:
        raise RuntimeError("Source-built base DQI hash mismatch")
    if file_sha256(base_invsqrt) != INVSQRT_SHA256:
        raise RuntimeError("Source-built Invsqrt hash mismatch")

    work = OUT / "work"
    work.mkdir()
    public_loaders = work / "public_loaders"
    public_loaders.mkdir()
    submission_dir = OUT / "submission" / "dfthcsos"
    submission_dir.mkdir(parents=True)
    for index in range(15):
        source = source_output / "dfthcsos" / f"angle_k_{index}.kmb"
        shutil.copyfile(source, public_loaders / source.name)
        shutil.copyfile(source, submission_dir / source.name)

    raw_table = work / "table_maoxin_v4.npz"
    table_hash = extract_table(input_root, competition, raw_table)
    shutil.copyfile(base_invsqrt, OUT / "submission" / "invsqrt.kmb")
    dqi_edit_summary = {"rewrites_applied": 0, "sha256": file_sha256(base_dqi)}
    shutil.copyfile(base_dqi, OUT / "submission" / "dqi.kmb")
    if dqi_edit_summary["sha256"] != BASE_DQI_SHA256:
        raise RuntimeError("Source-built DQI output hash mismatch")
    chemistry_summary = build_chemistry(raw_table, work, OUT / "submission", kickmix)

    verifier_env = dict(env)
    results = {
        "chemistry_default": run_verifier(
            ["dfthcsos/verify.py", str(submission_dir)],
            verifier_dir,
            verifier_env,
            OUT / "verify-chemistry-default.log",
        ),
        "chemistry_salt_42": run_verifier(
            ["dfthcsos/verify.py", str(submission_dir), "--salt", "42"],
            verifier_dir,
            verifier_env,
            OUT / "verify-chemistry-salt-42.log",
        ),
        "invsqrt": run_verifier(
            ["invsqrt/verify_submission_invsqrt.py", str(OUT / "submission" / "invsqrt.kmb"), "--max-workers", "4"],
            verifier_dir,
            verifier_env,
            OUT / "verify-invsqrt.log",
        ),
        "dqi": run_verifier(
            ["dqi/verify_submission_dqi.py", str(OUT / "submission" / "dqi.kmb"), "--max-workers", "4"],
            verifier_dir,
            verifier_env,
            OUT / "verify-dqi.log",
        ),
    }
    scores = {
        "invsqrt": results["invsqrt"]["result"]["score"],
        "dqi": results["dqi"]["result"]["score"],
        "dfthcsos": results["chemistry_default"]["result"]["score"],
    }
    verifier_geometric_score = math.prod(
        REFERENCES[name] / scores[name] for name in REFERENCES
    ) ** (1 / 3)
    archive_path = Path("/kaggle/working/submission.zip")
    member_hashes = write_archive(OUT / "submission", archive_path)
    receipt = {
        "experiment": "exp-074",
        "status": "PASS",
        "submission_status": "NOT_SUBMITTED",
        "source": {
            "tony_li_dataset": DATASET_SLUG,
            "tony_li_file_count": file_count,
            "tony_li_dataset_fingerprint": fingerprint,
            "maoxin_raw_parameter_table_sha256": table_hash,
            "goodpjw_notebook": "goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25564",
            "goodpjw_notebook_version": 20,
            "goodpjw_notebook_sha256": "ea7323f8536747c7775397e718f42745db802dacf4dcd24a5ead07baa9ed3420",
            "compiled_input_circuits_read": 0,
            "base_loader_kmbs_compiled_from_source": 15,
            "source_generator_seconds": build_seconds,
            "dqi_build": dqi_edit_summary,
            "chemistry": chemistry_summary,
        },
        "verifiers": results,
        "score": {
            "verifier_geometric_score": verifier_geometric_score,
            "verifier_component_scores": scores,
            "is_public_leaderboard_projection": False,
        },
        "archive": {
            "path": str(archive_path),
            "sha256": file_sha256(archive_path),
            "bytes": archive_path.stat().st_size,
            "members": member_hashes,
        },
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
