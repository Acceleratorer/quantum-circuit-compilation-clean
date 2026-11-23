"""Rebuild Syed v25 paired-plain DQI from its pinned source tree and verify it."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile


DATASET = Path("/kaggle/input/datasets/syed3000/vqcc-own-circuit-portfolio")
PACKAGE = DATASET / "dqi_generator" / "dqi_generator"
SOURCE = PACKAGE / "vendor" / "d70-source"
OUT = Path("/kaggle/working/exp063")
PACKAGE_COPY = Path("/kaggle/temp/exp063-source-package")
BUILD_OUT = Path("/kaggle/temp/exp063-build")
PROFILE = "paired-plain"
EXPECTED_ARCHIVE_SHA256 = "54fcce0d9846afae1fde0330e69803e4d9633a4e1ac4fcac49a7d1413ad20b45"
EXPECTED_OUTPUT_SHA256 = "fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5"
PACKAGE_SHA256 = {
    "README.md": "8c43097e3fa875365894d370e10e5ce79fb186a5c74bc76170f0e69250db974b",
    "build.py": "d400f69a899a7aac23d6abb5ed257c1cdbe96c192b964240d82e3022a4c497a9",
    "emit.py": "0e69f89841f30db5b2254ae4bfdf455ca0f2de3087f803b6f8fc5b6ec84ca11c",
    "lower_fredkin.py": "f7c9168e85490bd2747e13d0e7216c3ca5ebc0d47864827bf310984250d3ebfe",
    "manifest.json": "d6a8fa8169eacfa50bcc43f89affd64a9fc2368002a367477b21b8824bcd3483",
    "LICENSE": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "NOTICE": "b4e1cd477cca2cb53254e80ae35357b5609ddb61c4f10a0c724e107c1fdae042",
    "batch_dots.py": "a153d268800492fc31cf9ca0f734a46bb2252f5ec8edaaba1755512b742a80d3",
    "deferred_bulk.py": "77365693bd25f93527dfc023bddaebef26d8b4e78ebffc2b588c934dabb87b2c",
    "paired_converter.py": "87a3d3b6748a7e9786ed48249bd94ff118fe4c0594fba2f28378778797131d5f",
    "plain_pairs.py": "19bd443224369504a693b6452b2a006d6c2c19a3b9dd8a19f608f427d256c04b",
    "retained_head.py": "41dfe92a81782b81886408edf24ab355097fdd9102b663834af19c6dc9418fc6",
}
COMPETITION_SHA256 = {
    "kickmix/kickmix.so": "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e",
    "verifiers/dqi/__init__.py": "01c870aa9763f4e4357fc6654bff1d3296cec995bd0943f87b4a48946ada5b40",
    "verifiers/dqi/verify_submission_dqi.py": "f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65",
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def sanitized_env(competition_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    for key in tuple(env):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            marker in upper for marker in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            env.pop(key, None)
    engine_path = str(competition_root / "kickmix")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (engine_path, env.get("PYTHONPATH", ""))))
    env["VQCC_COMPETITION_DIR"] = str(competition_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def verified_source_files(manifest: dict) -> list[Path]:
    if not PACKAGE.is_dir() or not SOURCE.is_dir():
        raise RuntimeError(f"version 17 DQI source tree missing under {DATASET}")
    package_hashes = {name: sha256(PACKAGE / name) for name in PACKAGE_SHA256}
    if package_hashes != PACKAGE_SHA256:
        raise RuntimeError(f"upstream package hash mismatch: {package_hashes}")

    entries = list(SOURCE.rglob("*"))
    symlinks = [p.relative_to(SOURCE).as_posix() for p in entries if p.is_symlink()]
    if symlinks:
        raise RuntimeError(f"symlinks are not allowed in the pinned source tree: {symlinks[:8]}")
    files = sorted(p for p in entries if p.is_file())
    expected = manifest["files"]
    actual = {p.relative_to(SOURCE).as_posix() for p in files}
    if actual != set(expected):
        raise RuntimeError("source tree file list differs from the pinned manifest")
    for path in files:
        name = path.relative_to(SOURCE).as_posix()
        if sha256(path) != expected[name]:
            raise RuntimeError(f"source hash mismatch: {name}")
        if path.suffix.lower() in {".kmb", ".kmx", ".so", ".dll", ".exe"}:
            raise RuntimeError(f"compiled or executable file in source tree: {name}")
    return files


def source_tree_digest(files: list[Path]) -> tuple[str, int]:
    digest = hashlib.sha256()
    total_bytes = 0
    for path in files:
        relative = path.relative_to(SOURCE).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\n")
        total_bytes += path.stat().st_size
    return digest.hexdigest(), total_bytes


def locate_competition_root() -> tuple[Path, Path]:
    matches = [p for p in Path("/kaggle/input").rglob("verify_submission_dqi.py")
               if p.parent.name == "dqi"]
    if len(matches) != 1:
        raise RuntimeError(f"expected one official DQI verifier, found {len(matches)}")
    verifier = matches[0]
    root = verifier.parent.parent.parent
    if not (root / "kickmix" / "kickmix.so").is_file():
        raise RuntimeError(f"official Kickmix extension missing under {root}")
    return root, verifier


def main() -> None:
    if OUT.exists() or PACKAGE_COPY.exists() or BUILD_OUT.exists():
        raise RuntimeError("fresh exp-063 paths expected; refusing to reuse stale files")

    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("archive_sha256") != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("upstream source archive claim changed")
    if manifest.get("outputs", {}).get(PROFILE) != EXPECTED_OUTPUT_SHA256:
        raise RuntimeError("published candidate hash changed")
    files = verified_source_files(manifest)
    tree_sha256, source_bytes = source_tree_digest(files)
    competition_root, verifier = locate_competition_root()
    competition_hashes = {}
    for host, expected_hash in COMPETITION_SHA256.items():
        path = competition_root / host
        if not path.is_file() or sha256(path) != expected_hash:
            raise RuntimeError(f"official competition input changed: {host}")
        competition_hashes[host] = expected_hash
    verifier_hash = sha256(verifier)
    if verifier_hash != COMPETITION_SHA256["verifiers/dqi/verify_submission_dqi.py"]:
        raise RuntimeError("official verifier hash differs from the pinned competition input")

    source_report = {
        "status": "SOURCE_TREE_HASH_REVERIFIED",
        "dataset": "syed3000/vqcc-own-circuit-portfolio",
        "dataset_version": 17,
        "license": "Apache-2.0",
        "source_tree_files": len(files),
        "source_tree_bytes": source_bytes,
        "source_tree_sha256": tree_sha256,
        "compiled_circuit_inputs_read": False,
        "profile": PROFILE,
        "published_output_sha256": EXPECTED_OUTPUT_SHA256,
        "official_verifier_sha256": verifier_hash,
        "static_scan_executed_code": False,
    }
    OUT.mkdir(parents=True)
    (OUT / "source_audit.json").write_text(json.dumps(source_report, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(PACKAGE / "LICENSE", OUT / "UPSTREAM-LICENSE.txt")
    shutil.copyfile(PACKAGE / "NOTICE", OUT / "UPSTREAM-NOTICE.txt")

    PACKAGE_COPY.mkdir(parents=True)
    (PACKAGE_COPY / "vendor").mkdir()
    for name in PACKAGE_SHA256:
        shutil.copyfile(PACKAGE / name, PACKAGE_COPY / name)
    archive = PACKAGE_COPY / "vendor" / "d70-source.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for path in files:
            zipped.write(path, path.relative_to(SOURCE).as_posix())
    reconstructed_archive_sha256 = sha256(archive)
    manifest["archive_sha256"] = reconstructed_archive_sha256
    (PACKAGE_COPY / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    provenance = {
        "dataset": "syed3000/vqcc-own-circuit-portfolio",
        "dataset_version": 17,
        "license": "Apache-2.0",
        "upstream_archive_sha256_claim": EXPECTED_ARCHIVE_SHA256,
        "upstream_archive_present": False,
        "reconstructed_archive_sha256": reconstructed_archive_sha256,
        "reconstructed_archive_contents_verified_against_manifest": True,
        "source_tree_files": len(files),
        "source_tree_bytes": source_report["source_tree_bytes"],
        "source_tree_sha256": source_report["source_tree_sha256"],
        "candidate_profile": PROFILE,
        "candidate_sha256_expected": EXPECTED_OUTPUT_SHA256,
        "competition_input_sha256": competition_hashes,
        "official_verifier_sha256": verifier_hash,
        "public_circuit_binaries_read": False,
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    env = sanitized_env(competition_root)
    builder = PACKAGE_COPY / "build.py"
    build_stdout, build_stderr = OUT / "build.stdout", OUT / "build.stderr"
    start = time.monotonic()
    with build_stdout.open("w", encoding="utf-8") as stdout, build_stderr.open("w", encoding="utf-8") as stderr:
        built = subprocess.run([sys.executable, "-B", str(builder), "--profile", PROFILE, "--out", str(BUILD_OUT)],
                               cwd=PACKAGE_COPY, env=env, stdout=stdout, stderr=stderr)
    build_seconds = time.monotonic() - start
    if built.returncode:
        raise RuntimeError(f"source build failed ({built.returncode}); inspect build.stdout/build.stderr")

    generated = BUILD_OUT / "dqi.kmb"
    candidate_sha256 = sha256(generated)
    if candidate_sha256 != EXPECTED_OUTPUT_SHA256:
        raise RuntimeError(f"candidate hash mismatch: {candidate_sha256}")
    candidate = OUT / "dqi.kmb"
    shutil.copyfile(generated, candidate)
    shutil.copyfile(BUILD_OUT / "build.json", OUT / "build.json")

    verify_stdout, verify_stderr = OUT / "verify.stdout.json", OUT / "verify.stderr"
    verify_command = [sys.executable, "-B", str(verifier), str(candidate), "--max-workers", "1"]
    verify_start = time.monotonic()
    with verify_stdout.open("w", encoding="utf-8") as stdout, verify_stderr.open("w", encoding="utf-8") as stderr:
        verified = subprocess.run(verify_command, cwd=competition_root, env=env, stdout=stdout, stderr=stderr)
    verification_seconds = time.monotonic() - verify_start
    verification = json.loads(verify_stdout.read_text(encoding="utf-8"))
    if verified.returncode or verification.get("status") != "PASS":
        raise RuntimeError(f"official verifier failed ({verified.returncode}): {verification}")
    if verification.get("circuit_sha256") != EXPECTED_OUTPUT_SHA256:
        raise RuntimeError("official verifier reported a different circuit hash")

    result = {
        "experiment": "exp-063",
        "build_seconds": build_seconds,
        "verification_seconds": verification_seconds,
        "candidate_sha256": candidate_sha256,
        "official_verification": verification,
        "status": "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS",
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
