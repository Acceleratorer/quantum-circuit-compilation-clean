"""Rebuild the licensed Syed v17 invsqrt source tree, then run the official verifier."""
from __future__ import annotations

import collections
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


DATASET = Path("/kaggle/input/datasets/syed3000/vqcc-own-circuit-portfolio")
PACKAGE = DATASET / "invsqrt_generator" / "invsqrt_generator"
SOURCE = PACKAGE / "syed_source"
OUT = Path("/kaggle/working/exp062")
PACKAGE_COPY = Path("/kaggle/temp/exp062-source-package")
BUILD_OUT = Path("/kaggle/temp/exp062-build")
EXPECTED_CIRCUIT_SHA256 = "70fe5f79d56bd48cd8fc9602757a0520b4d11859967627906cccb3dec25b7692"
EXPECTED_ARCHIVE_SHA256 = "4f9fabdcc7618d6ec93259b84b6a9f08d2e02efa6bf29cc54b47470f98e3ec3c"
EXPECTED_SOURCE_BYTES = 31_891_406
EXPECTED_SOURCE_FILES = 1_019
PACKAGE_SHA256 = {
    "build.py": "30d9b8f51877ce7d2efc9ce6faf7dbb03e9bc5de16b305101fe91172a547d6ed",
    "coefficient_phase.json": "bb1820e62890e401068d7461e715876290649e779d562a73d0c1616938452020",
    "coefficient_windows.py": "a72d6aedec56354a755d994af47f02eaeb2c893d372754b1117ee08290aaf116",
    "finish_f16.py": "f3d12ff6aedf5283386e8e7f363f6121a67a6ffb41340ab9906f739b6df6408a",
    "LICENSE": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "NOTICE": "51a1cacf35155c1152a874925463b4ab25016bc661d78f60143ca6d8cd167b2b",
    "owner_lineage.py": "7779b72f90cf092a4c04acc23816ef1b4628bb24c1080fe68daa6c05f82ec7e8",
    "prepare.py": "f25bf2f5448555fbe9b84b615e3b0ee2dfe8ddade7d4f66dfea2aadfbf946d1e",
    "README.md": "76b1780b19cca8392480d26f0974677b0ec3a4424435590e2780e7b2eac9e205",
}
ARCHIVE_BLOCK = (
    "    assert digest(HERE/'syed_source.zip')=='"
    "1c3d7d7b66ad4df27ad216d03c3b77a095554580e84e5363b366f4512b7d241d'\n"
    "    with zipfile.ZipFile(HERE/'syed_source.zip')as z:z.extractall(work)\n"
)
TREE_BLOCK = (
    "    source_tree=HERE/'syed_source'\n"
    "    shutil.copytree(source_tree,work,dirs_exist_ok=True)\n"
)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_tree_digest(root: Path):
    digest = hashlib.sha256()
    files = sorted(p for p in root.rglob("*") if p.is_file())
    suffixes = collections.Counter(p.suffix.lower() or "[none]" for p in files)
    total = 0
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
        total += path.stat().st_size
    return digest.hexdigest(), files, total, dict(sorted(suffixes.items()))


def sanitized_env():
    env = os.environ.copy()
    for key in ("KAGGLE_API_TOKEN", "KAGGLE_KEY", "KAGGLE_USERNAME"):
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def ignore_unused_or_binary(directory, names):
    parent = Path(directory)
    ignored = {"search"} if parent == PACKAGE and "search" in names else set()
    for name in names:
        child = parent / name
        if child.is_file() and child.suffix.lower() in {".bin", ".kmb", ".kmx", ".npz", ".so", ".dll", ".exe", ".zip"}:
            ignored.add(name)
    return ignored


def restore_missing_json_gzip(package_copy: Path):
    records = []
    seen = set()
    source_root = package_copy / "syed_source"
    package_root = package_copy.resolve()

    def restore(target: Path, plain: Path):
        payload = plain.read_bytes()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.compress(payload, mtime=0))
        assert gzip.decompress(target.read_bytes()) == payload
        key = target.relative_to(package_copy).as_posix()
        if key not in seen:
            records.append({
                "derived": key,
                "source": plain.relative_to(package_copy).as_posix(),
                "source_sha256": sha256(plain),
                "derived_sha256": sha256(target),
                "bytes": target.stat().st_size,
            })
            seen.add(key)

    for script in package_copy.rglob("*.py"):
        text = script.read_text(encoding="utf-8", errors="replace")
        for reference in re.findall(r"['\"]([^'\"]+\.json\.gz)['\"]", text):
            relative = Path(reference)
            if relative.is_absolute():
                continue
            for base in (source_root, script.parent, package_copy):
                target = base / relative
                if not target.resolve().is_relative_to(package_root):
                    continue
                if target.is_file():
                    break
                plain = target.with_suffix("")
                if plain.is_file():
                    restore(target, plain)
                    break
            if len(relative.parts) == 1:
                plain_name = relative.with_suffix("").name
                for plain in source_root.rglob(plain_name):
                    if plain.is_file():
                        target = plain.with_suffix(".json.gz")
                        if not target.is_file():
                            restore(target, plain)
    return records


def main():
    if not PACKAGE.is_dir() or not SOURCE.is_dir():
        raise RuntimeError(f"v17 source tree missing under {DATASET}")
    if OUT.exists() or PACKAGE_COPY.exists() or BUILD_OUT.exists():
        raise RuntimeError("fresh Kaggle working paths expected; refusing to reuse stale build files")
    OUT.mkdir(parents=True)

    package_hashes = {name: sha256(PACKAGE / name) for name in PACKAGE_SHA256}
    if package_hashes != PACKAGE_SHA256:
        raise RuntimeError(f"upstream wrapper hash mismatch: {package_hashes}")

    tree_sha, source_files, source_bytes, suffixes = source_tree_digest(SOURCE)
    if len(source_files) != EXPECTED_SOURCE_FILES or source_bytes != EXPECTED_SOURCE_BYTES:
        raise RuntimeError(f"unexpected source tree shape: {len(source_files)} files, {source_bytes} bytes")
    forbidden = [p.relative_to(SOURCE).as_posix() for p in source_files
                 if p.suffix.lower() in {".kmb", ".kmx", ".bin", ".npz", ".so", ".dll", ".exe"}]
    if forbidden:
        raise RuntimeError(f"circuit or executable files found in source tree: {forbidden[:8]}")

    manifest = DATASET / "SOURCES.sha256"
    archive_claim = None
    if manifest.is_file():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == "invsqrt_generator.zip":
                archive_claim = parts[0]
    if archive_claim != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError(f"outer source manifest changed: {archive_claim}")

    package_circuit_files = [p for p in PACKAGE.rglob("*") if p.is_file() and p.suffix.lower() in {".kmb", ".kmx"}]
    if package_circuit_files:
        raise RuntimeError(f"public circuit files present in package tree: {package_circuit_files[:8]}")
    shutil.copytree(PACKAGE, PACKAGE_COPY, ignore=ignore_unused_or_binary)
    derived_gzip_inputs = restore_missing_json_gzip(PACKAGE_COPY)
    copied_circuits = [p for p in PACKAGE_COPY.rglob("*")
                       if p.is_file() and p.suffix.lower() in {".kmb", ".kmx", ".bin", ".npz", ".so", ".dll", ".exe", ".zip"}]
    if copied_circuits:
        raise RuntimeError(f"unexpected binary artifacts copied: {copied_circuits[:8]}")
    builder = PACKAGE_COPY / "build.py"
    builder_text = builder.read_text(encoding="utf-8")
    if builder_text.count(ARCHIVE_BLOCK) != 1:
        raise RuntimeError("expected source-archive extraction block not found exactly once")
    builder.write_text(builder_text.replace(ARCHIVE_BLOCK, TREE_BLOCK), encoding="utf-8")

    provenance = {
        "dataset": "syed3000/vqcc-own-circuit-portfolio",
        "dataset_version": 17,
        "outer_archive_sha256_claim": archive_claim,
        "outer_archive_present": (DATASET / "invsqrt_generator.zip").is_file(),
        "inner_archive_present": (SOURCE / "syed_source.zip").is_file(),
        "source_tree_files": len(source_files),
        "source_tree_bytes": source_bytes,
        "source_tree_suffixes": suffixes,
        "source_tree_sha256": tree_sha,
        "source_tree_digest": "sha256 over sorted relative path, NUL, file SHA-256, newline",
        "upstream_package_sha256": package_hashes,
        "copied_package_search_tree": False,
        "copied_package_circuit_binaries": False,
        "restored_gzip_inputs": derived_gzip_inputs,
        "patched_build_py_sha256": sha256(builder),
        "adaptation": "copied the Kaggle-published extracted syed_source tree instead of the unavailable nested zip",
        "upstream_license": "Apache-2.0",
        "circuit_binary_inputs_read": False,
    }
    (OUT / "source_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    shutil.copyfile(PACKAGE_COPY / "LICENSE", OUT / "UPSTREAM-LICENSE.txt")
    shutil.copyfile(PACKAGE_COPY / "NOTICE", OUT / "UPSTREAM-NOTICE.txt")

    env = sanitized_env()
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", "kickmix==1.0.0"],
                   check=True, env=env)
    versions = {name: importlib.metadata.version(name) for name in ("kickmix", "numpy", "scipy")}
    build_stdout = OUT / "build.stdout"
    build_stderr = OUT / "build.stderr"
    start = time.monotonic()
    with build_stdout.open("w", encoding="utf-8") as stdout, build_stderr.open("w", encoding="utf-8") as stderr:
        built = subprocess.run([sys.executable, "-B", str(builder), "--out", str(BUILD_OUT)],
                               cwd=PACKAGE_COPY, env=env, stdout=stdout, stderr=stderr)
    build_seconds = time.monotonic() - start
    if built.returncode:
        raise RuntimeError(f"source build failed ({built.returncode}); inspect build.stdout/build.stderr")

    generated = BUILD_OUT / "invsqrt.kmb"
    candidate_sha = sha256(generated)
    if candidate_sha != EXPECTED_CIRCUIT_SHA256:
        raise RuntimeError(f"source build hash mismatch: {candidate_sha}")
    shutil.copyfile(generated, OUT / "invsqrt.kmb")
    shutil.copyfile(BUILD_OUT / "build_receipt.json", OUT / "build_receipt.json")

    verifier_scripts = [p for p in Path("/kaggle/input").rglob("verify_submission_invsqrt.py")
                        if p.parent.name == "invsqrt"]
    if len(verifier_scripts) != 1:
        raise RuntimeError(f"expected one official verifier, found {len(verifier_scripts)}")
    verifier = verifier_scripts[0]
    verify_command = [sys.executable, "-I", "-B", "invsqrt/verify_submission_invsqrt.py", str(OUT / "invsqrt.kmb")]
    verify_stdout = OUT / "verify_full.json"
    verify_stderr = OUT / "verify.stderr"
    verify_start = time.monotonic()
    with verify_stdout.open("w", encoding="utf-8") as stdout, verify_stderr.open("w", encoding="utf-8") as stderr:
        verified = subprocess.run(verify_command, cwd=verifier.parent.parent, env=env, stdout=stdout, stderr=stderr)
    verify_seconds = time.monotonic() - verify_start
    verification = json.loads(verify_stdout.read_text(encoding="utf-8"))
    if verified.returncode or verification.get("status") != "PASS":
        raise RuntimeError(f"official verifier failed ({verified.returncode}): {verification}")
    if verification.get("circuit_sha256") != EXPECTED_CIRCUIT_SHA256:
        raise RuntimeError("official verifier reported a different circuit hash")

    result = {
        "experiment": "exp-062",
        "build_seconds": build_seconds,
        "verification_seconds": verify_seconds,
        "versions": versions,
        "candidate_sha256": candidate_sha,
        "official_verifier_sha256": sha256(verifier),
        "official_verification": verification,
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
