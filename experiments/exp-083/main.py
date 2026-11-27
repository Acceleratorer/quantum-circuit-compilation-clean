"""Build a source-owned exp-065 portfolio with V20 chemistry loaders on Kaggle."""

from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import runpy
import shutil
import stat
import subprocess
import sys
import time
import zipfile


# BEGIN GENERATED SOURCE BUNDLE
BUNDLE_SHA256 = ""
BUNDLE_MANIFEST = {}
BUNDLE_B85 = ""
# END GENERATED SOURCE BUNDLE


OUT = Path("/kaggle/working/exp083")
BUNDLE_ROOT = Path("/kaggle/working/exp083-source")
WORKING_ROOT = Path("/kaggle/working")
TEMP_ROOT = Path("/kaggle/temp")
TABLE_SHA256 = "ec85d969811623b5b4c7e3fff26fef2151bafedaa9a4741cb978e56ff34fbba1"
EXPECTED_INVSQRT_SHA256 = "70fe5f79d56bd48cd8fc9602757a0520b4d11859967627906cccb3dec25b7692"
EXPECTED_DQI_SHA256 = "fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5"
REFERENCES = {
    "invsqrt": 2076774.233715282,
    "dqi": 24439463583672.93,
    "dfthcsos": 3355599588.3155375,
}
BEST_ELIGIBLE_SCORE = 28.71611


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unpack_source_bundle() -> Path:
    if not BUNDLE_B85 or not BUNDLE_SHA256 or not BUNDLE_MANIFEST:
        raise RuntimeError("Run package_kernel.py before pushing this source to Kaggle")
    if BUNDLE_ROOT.exists():
        raise RuntimeError(f"Refusing to reuse source bundle directory: {BUNDLE_ROOT}")
    payload = base64.b85decode(BUNDLE_B85.encode("ascii"))
    if sha256(payload) != BUNDLE_SHA256:
        raise RuntimeError("Embedded source bundle hash mismatch")
    BUNDLE_ROOT.mkdir(parents=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(BUNDLE_MANIFEST):
            raise RuntimeError("Embedded source bundle member set mismatch")
        for info in archive.infolist():
            relative = PurePosixPath(info.filename)
            mode = (info.external_attr >> 16) & 0o170000
            if relative.is_absolute() or ".." in relative.parts or info.is_dir() or mode == stat.S_IFLNK:
                raise RuntimeError(f"Unsafe embedded source path: {info.filename}")
            data = archive.read(info)
            if sha256(data) != BUNDLE_MANIFEST[info.filename]:
                raise RuntimeError(f"Embedded source hash mismatch: {info.filename}")
            target = BUNDLE_ROOT.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return BUNDLE_ROOT


def run_source_builder(name: str, script: Path) -> None:
    if not script.is_file():
        raise RuntimeError(f"Source builder is missing: {script}")
    stdout_path, stderr_path = OUT / f"{name}.stdout", OUT / f"{name}.stderr"
    argv = sys.argv[:]
    try:
        sys.argv = [str(script)]
        with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
            "w", encoding="utf-8"
        ) as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                runpy.run_path(str(script), run_name="__main__")
    finally:
        sys.argv = argv


def locate_competition(input_root: Path) -> tuple[Path, Path]:
    matches = [
        path
        for path in input_root.rglob("verify_submission_dqi.py")
        if path.parent.name == "dqi"
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one official competition verifier tree; found {len(matches)}")
    verifier = matches[0]
    competition = verifier.parents[2]
    if not (competition / "kickmix" / "kickmix.so").is_file():
        raise RuntimeError("Official Kickmix extension is missing")
    return competition, verifier.parent.parent


def extract_table(input_root: Path, competition: Path, destination: Path) -> str:
    """Read only the pinned raw parameter NPZ, never a compiled input circuit."""
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
        raise RuntimeError("Pinned Maoxin raw parameter table was not attached")
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
    if run.returncode or payload is None or payload.get("status") != "PASS":
        raise RuntimeError(f"Official verifier failed ({run.returncode}); inspect {output}")
    return {"seconds": round(time.monotonic() - started, 2), "result": payload}


def write_archive(submission_dir: Path, archive_path: Path) -> dict[str, str]:
    members = [
        "invsqrt.kmb",
        "dqi.kmb",
        *[f"dfthcsos/angle_k_{index}.kmb" for index in range(15)],
        "dfthcsos/submission.npz",
    ]
    hashes: dict[str, str] = {}
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


def remove_tree(path: Path, allowed_root: Path) -> None:
    if not path.exists():
        return
    if path.is_symlink() or not path.resolve().is_relative_to(allowed_root.resolve()):
        raise RuntimeError(f"Refusing unsafe cleanup path: {path}")
    shutil.rmtree(path)


def cleanup_intermediates() -> None:
    for path in (
        BUNDLE_ROOT,
        WORKING_ROOT / "exp062",
        WORKING_ROOT / "exp063",
        WORKING_ROOT / "exp064",
        TEMP_ROOT / "exp062-source-package",
        TEMP_ROOT / "exp062-build",
        TEMP_ROOT / "exp063-source-package",
        TEMP_ROOT / "exp063-build",
        TEMP_ROOT / "exp064-source-package",
        TEMP_ROOT / "exp064-build",
    ):
        root = TEMP_ROOT if path.is_relative_to(TEMP_ROOT) else WORKING_ROOT
        remove_tree(path, root)
    for child in tuple(OUT.iterdir()):
        if child.name == "receipt.json":
            continue
        if child.is_dir():
            remove_tree(child, OUT)
        elif child.is_file():
            child.unlink()


def main() -> None:
    submission_archive = WORKING_ROOT / "submission.zip"
    if OUT.exists() or BUNDLE_ROOT.exists() or submission_archive.exists():
        raise RuntimeError("Expected fresh Kaggle output paths; refusing to overwrite")
    OUT.mkdir(parents=True)
    bundle_root = unpack_source_bundle()

    builders = (
        ("exp062", bundle_root / "source" / "exp062_rebuild_verify.py"),
        ("exp063", bundle_root / "source" / "exp063_rebuild_verify.py"),
        ("exp064", bundle_root / "source" / "exp064_rebuild_verify.py"),
    )
    for name, script in builders:
        run_source_builder(name, script)

    exp062 = json.loads((WORKING_ROOT / "exp062" / "result.json").read_text(encoding="utf-8"))
    exp063 = json.loads((WORKING_ROOT / "exp063" / "result.json").read_text(encoding="utf-8"))
    exp064 = json.loads((WORKING_ROOT / "exp064" / "result.json").read_text(encoding="utf-8"))
    if exp062.get("candidate_sha256") != EXPECTED_INVSQRT_SHA256:
        raise RuntimeError("Source-built Invsqrt does not match the verified exp-065 member")
    if exp063.get("candidate_sha256") != EXPECTED_DQI_SHA256:
        raise RuntimeError("Source-built DQI does not match the verified exp-065 member")
    if exp062.get("official_verification", {}).get("status") != "PASS":
        raise RuntimeError("The Invsqrt source rebuild did not pass the official verifier")
    if any(
        result.get("status") != "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS"
        for result in (exp063, exp064)
    ):
        raise RuntimeError("One of the three source component rebuilds did not pass")

    input_root = Path("/kaggle/input")
    competition, verifier_dir = locate_competition(input_root)
    kickmix_dir = competition / "kickmix"
    sys.path.insert(0, str(kickmix_dir))
    import kickmix

    work = OUT / "work"
    work.mkdir()
    public_loaders = work / "public_loaders"
    public_loaders.mkdir()
    submission_dir = OUT / "submission"
    chemistry_dir = submission_dir / "dfthcsos"
    chemistry_dir.mkdir(parents=True)
    source_chemistry = WORKING_ROOT / "exp064"
    for index in range(15):
        source = source_chemistry / f"angle_k_{index}.kmb"
        shutil.copyfile(source, public_loaders / source.name)
        shutil.copyfile(source, chemistry_dir / source.name)
    shutil.copyfile(WORKING_ROOT / "exp062" / "invsqrt.kmb", submission_dir / "invsqrt.kmb")
    shutil.copyfile(WORKING_ROOT / "exp063" / "dqi.kmb", submission_dir / "dqi.kmb")

    raw_table = work / "table_maoxin_v4.npz"
    table_hash = extract_table(input_root, competition, raw_table)
    if table_hash != TABLE_SHA256:
        raise RuntimeError("Extracted parameter table hash does not match the pin")
    sys.path.insert(0, str(bundle_root / "source"))
    from v20_build_chemistry import build_chemistry

    chemistry_summary = build_chemistry(raw_table, work, submission_dir, kickmix)
    env = sanitized_env([kickmix_dir, verifier_dir])
    verifiers = {
        "chemistry_default": run_verifier(
            ["dfthcsos/verify.py", str(chemistry_dir)],
            verifier_dir,
            env,
            OUT / "verify-chemistry-default.log",
        ),
        "chemistry_salt_42": run_verifier(
            ["dfthcsos/verify.py", str(chemistry_dir), "--salt", "42"],
            verifier_dir,
            env,
            OUT / "verify-chemistry-salt-42.log",
        ),
    }
    scores = {
        "invsqrt": exp062["official_verification"]["score"],
        "dqi": exp063["official_verification"]["score"],
        "dfthcsos": verifiers["chemistry_default"]["result"]["score"],
    }
    geometric_score = math.prod(REFERENCES[name] / scores[name] for name in REFERENCES) ** (1 / 3)
    archive_hashes: dict[str, str] = {}
    submission_status = "NOT_SUBMITTED"
    if geometric_score > BEST_ELIGIBLE_SCORE:
        archive_hashes = write_archive(submission_dir, submission_archive)
        submission_status = "READY_FOR_SUBMISSION"

    receipt = {
        "experiment": "exp-083",
        "status": "PASS",
        "submission_status": submission_status,
        "sources": {
            "bundle_sha256": BUNDLE_SHA256,
            "bundle_file_sha256": BUNDLE_MANIFEST,
            "component_rebuilds": {
                "invsqrt": exp062,
                "dqi": exp063,
                "dfthcsos_base": exp064,
            },
            "v20_loader": chemistry_summary,
            "maoxin_parameter_table_sha256": table_hash,
            "compiled_circuit_inputs_read": False,
        },
        "verifiers": verifiers,
        "score": {
            "component_scores": scores,
            "verifier_geometric_mean": geometric_score,
            "best_eligible_baseline": BEST_ELIGIBLE_SCORE,
            "improvement_over_baseline": geometric_score - BEST_ELIGIBLE_SCORE,
            "is_public_leaderboard_projection": False,
        },
        "archive": {
            "path": str(submission_archive) if archive_hashes else None,
            "sha256": file_sha256(submission_archive) if archive_hashes else None,
            "bytes": submission_archive.stat().st_size if archive_hashes else None,
            "member_count": len(archive_hashes),
            "members": archive_hashes,
        },
    }
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    cleanup_intermediates()
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
