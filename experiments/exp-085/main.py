"""Rebuild the pinned v155 inverse-square-root generator on Kaggle."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time


SOURCE_ARCHIVE_SHA256 = "5d34399e677402091cd18505637c88711dcce9a64ad66e594f1dd1e8651ef405"
EXPECTED_CIRCUIT_SHA256 = "b4ba2126a1ac435af2ab4e8e8394eb79bdf9dfae1ccb2aad06e5fad177e47608"
SOURCE_ARCHIVE_BYTES = 2_130_989
WORK = Path("/kaggle/working")
SOURCE_ROOT = WORK / "exp085-source"
BUILD_ROOT = WORK / "exp085-build"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def find_source_archive() -> Path:
    matches = [
        path
        for path in Path("/kaggle/input").rglob("isr_source_targz.bin")
        if path.is_file()
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one pinned ISR source archive, found {len(matches)}")
    path = matches[0]
    if path.stat().st_size != SOURCE_ARCHIVE_BYTES or sha256(path) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("The attached ISR source archive differs from the pinned release")
    return path


def extract_source(archive_path: Path) -> None:
    if SOURCE_ROOT.exists():
        raise RuntimeError(f"Refusing to reuse source path {SOURCE_ROOT}")
    SOURCE_ROOT.mkdir()
    root = SOURCE_ROOT.resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate source archive paths")
        for member in members:
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(f"Unsafe source archive path: {member.name}")
            destination = SOURCE_ROOT.joinpath(*relative.parts)
            if not destination.resolve().is_relative_to(root):
                raise RuntimeError(f"Source archive path escaped its root: {member.name}")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"Could not read source archive member: {member.name}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source, destination.open("xb") as output:
                    shutil.copyfileobj(source, output)
            else:
                raise RuntimeError(f"Unsupported source archive member: {member.name}")


def main() -> None:
    for path in (SOURCE_ROOT, BUILD_ROOT, WORK / "invsqrt.kmb", WORK / "receipt.json"):
        if path.exists():
            raise RuntimeError(f"Expected fresh output path; refusing to overwrite {path}")

    started = time.monotonic()
    source_archive = find_source_archive()
    extract_source(source_archive)
    package = SOURCE_ROOT / "isr_source"
    build_script = package / "build.py"
    if not build_script.is_file():
        raise RuntimeError("Pinned ISR release does not contain build.py")

    env = os.environ.copy()
    for key in tuple(env):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            marker in upper
            for marker in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["VERIFY"] = "0"
    env["S5LEND"] = "1"
    for key in ("SSH_AUTH_SOCK", "SSH_AGENT_PID", "GIT_SSH", "GIT_SSH_COMMAND"):
        env.pop(key, None)

    run = subprocess.run(
        [sys.executable, "-B", str(build_script), str(BUILD_ROOT)],
        cwd=package,
        env=env,
        capture_output=True,
        text=True,
    )
    if run.returncode:
        raise RuntimeError(f"Pinned source build failed ({run.returncode}):\n{run.stdout[-3000:]}\n{run.stderr[-3000:]}")

    candidate = BUILD_ROOT / "invsqrt.kmb"
    if not candidate.is_file() or sha256(candidate) != EXPECTED_CIRCUIT_SHA256:
        raise RuntimeError("Source build did not reproduce the pinned Invsqrt circuit hash")

    source_result_path = (
        package
        / "repo/experiments/isr/iterations/772_isr_769_dial_w8/trials/001_officials/result.json"
    )
    source_result = json.loads(source_result_path.read_text(encoding="utf-8"))
    checks = [source_result["official_verification"], source_result["official_confirmation"]]
    for check in checks:
        result = check["result"]
        if result.get("status") != "PASS" or result.get("circuit_sha256") != EXPECTED_CIRCUIT_SHA256:
            raise RuntimeError("Published official evidence does not match the rebuilt circuit")

    shutil.copyfile(candidate, WORK / "invsqrt.kmb")
    shutil.copyfile(BUILD_ROOT / "isr_build_log.json", WORK / "isr_build_log.json")
    shutil.copytree(BUILD_ROOT / "LICENSES", WORK / "LICENSES")
    receipt = {
        "experiment": "exp-085",
        "status": "SOURCE_BUILD_HASH_MATCH",
        "source_dataset": "dziyanavalenta/q2026-v155-isr-generator",
        "source_archive_sha256": sha256(source_archive),
        "source_archive_bytes": source_archive.stat().st_size,
        "circuit_sha256": sha256(WORK / "invsqrt.kmb"),
        "circuit_bytes": (WORK / "invsqrt.kmb").stat().st_size,
        "source_build_seconds": round(time.monotonic() - started, 2),
        "published_official_results": [check["result"] for check in checks],
        "published_official_evidence_only": True,
        "compiled_circuit_used_as_build_input": False,
    }
    (WORK / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(SOURCE_ROOT)
    shutil.rmtree(BUILD_ROOT)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
