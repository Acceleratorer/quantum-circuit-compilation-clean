"""Rebuild the pinned dfthcsos sources and run the official verifier."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import time


DATASET = Path("/kaggle/input/datasets/syed3000/vqcc-own-circuit-portfolio")
PACKAGE = DATASET / "dfthcsos_generator" / "dfthcsos_generator"
COMPETITION = Path(
    "/kaggle/input/competitions/google-verifiable-quantum-circuit-compilation"
)
VERIFIER = COMPETITION / "verifiers/dfthcsos/verify.py"
OUT = Path("/kaggle/working/exp064")
PACKAGE_COPY = Path("/kaggle/temp/exp064-source-package")
BUILD = Path("/kaggle/temp/exp064-build")
BUILD_OUT, SOURCE_OUT = BUILD / "circuits", BUILD / "sources"

EXPECTED = {
    "FILE_HASHES.json": "4ea1f2c26f8467f362c2dc3fa91ff8494268874db58cdcd29ba9189ddcd22cd7",
    "manifest.json": "08bc05b1eea5a25a614c38e7ba93648c3e2adbcf97ec5c986810763f589a27db",
    "rebuild.py": "b26833d6baa662df2d24b58ad98ded7d26be08602e5996e316f584e73d26f879",
    "submission.npz": "07f81f5f31341785821c773483e7bbeb7b7b087512dd65dc8c38589285373dbf",
    "verifier.py": "0775be7a528922367caebe9e4d051d6199811f1aefeaa4b793eaaa4621b8ec9d",
    "kickmix.so": "c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e",
}

blocked_reads: list[str] = []


def block_input_circuits(event: str, args: tuple[object, ...]) -> None:
    if event != "open" or not args or isinstance(args[0], int):
        return
    path = os.fsdecode(args[0]).replace("\\", "/")
    if not path.startswith("/"):
        path = os.path.abspath(path).replace("\\", "/")
    if path.lower().startswith("/kaggle/input/") and path.lower().endswith((".kmb", ".kmx")):
        blocked_reads.append(path)
        raise PermissionError(f"Public input circuit reads are forbidden: {path}")


sys.addaudithook(block_input_circuits)


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, value: object) -> None:
    def encode(value: object) -> object:
        if hasattr(value, "item"):
            return value.item()  # type: ignore[no-any-return]
        raise TypeError(type(value).__name__)

    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=encode) + "\n")


def main() -> None:
    if any(path.exists() for path in (OUT, PACKAGE_COPY, BUILD)):
        raise RuntimeError("exp-064 paths must be fresh")

    for key in tuple(os.environ):
        upper = key.upper()
        if upper == "KAGGLE_USERNAME" or any(
            word in upper for word in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY", "ACCESS_KEY")
        ) or upper.endswith("_KEY"):
            os.environ.pop(key, None)
    os.environ.update(
        PYTHONDONTWRITEBYTECODE="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        VQCC_COMPETITION_DIR=str(COMPETITION),
    )
    sys.path[:0] = [str(COMPETITION / "verifiers"), str(COMPETITION / "kickmix")]

    file_hashes_path = PACKAGE / "FILE_HASHES.json"
    if sha256(file_hashes_path) != EXPECTED["FILE_HASHES.json"]:
        raise RuntimeError("pinned source hash manifest changed")
    file_hashes = json.loads(file_hashes_path.read_text(encoding="utf-8"))["files"]
    source_files = [
        "FILE_HASHES.json", "LICENSE", "NOTICE", "manifest.json", "rebuild.py", "submission.npz",
        *sorted(name for name in file_hashes if name.startswith("compiler/")),
        *(f"plans/angle_k_{k}.json" for k in range(15)),
    ]
    if len(source_files) != 35:
        raise RuntimeError(f"unexpected source file set: {len(source_files)} files")

    source_hashes: dict[str, str] = {}
    source_bytes = 0
    for name in source_files:
        path = PACKAGE / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"missing or symlinked source file: {name}")
        digest = sha256(path)
        if name in EXPECTED and digest != EXPECTED[name]:
            raise RuntimeError(f"pinned source hash changed: {name}")
        if name != "FILE_HASHES.json" and file_hashes.get(name) != digest:
            raise RuntimeError(f"source file hash mismatch: {name}")
        source_hashes[name] = digest
        source_bytes += path.stat().st_size

    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("npz_sha256") != EXPECTED["submission.npz"] or len(manifest["loaders"]) != 15:
        raise RuntimeError("pinned manifest does not match the factorization and 15 loaders")

    import numpy as np

    with np.load(PACKAGE / "submission.npz", allow_pickle=False) as data:
        keys = {"U", "W", "H2_I", "H1_I", "Hsym_lower", "tree_edges", "angle_words"}
        if set(data.files) != keys or data["angle_words"].shape != (1220, 75):
            raise RuntimeError("source factorization NPZ schema changed")
        if data["tree_edges"].shape != (75, 2) or not np.all((data["angle_words"] >= 0) & (data["angle_words"] <= 255)):
            raise RuntimeError("source words or Givens tree are invalid")
        npz_schema = {key: [list(data[key].shape), str(data[key].dtype)] for key in sorted(keys)}

    if sha256(VERIFIER) != EXPECTED["verifier.py"]:
        raise RuntimeError("official dfthcsos verifier hash changed")
    if sha256(COMPETITION / "kickmix/kickmix.so") != EXPECTED["kickmix.so"]:
        raise RuntimeError("official Kickmix extension hash changed")

    tree = hashlib.sha256()
    for name in source_files:
        tree.update(name.encode() + b"\0" + source_hashes[name].encode() + b"\n")
    source_tree_sha256 = tree.hexdigest()

    OUT.mkdir(parents=True)
    PACKAGE_COPY.mkdir(parents=True)
    for name in source_files:
        destination = PACKAGE_COPY / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PACKAGE / name, destination)
    for name, dest in (("LICENSE", "UPSTREAM-LICENSE.txt"), ("NOTICE", "UPSTREAM-NOTICE.txt"), ("submission.npz", "submission.npz")):
        shutil.copyfile(PACKAGE / name, OUT / dest)

    source_audit = {
        "status": "PINNED_SOURCE_TREE_VERIFIED",
        "dataset": "syed3000/vqcc-own-circuit-portfolio",
        "dataset_version_claim": 17,
        "license": "Apache-2.0",
        "selected_source_files": len(source_files),
        "selected_source_bytes": source_bytes,
        "selected_source_tree_sha256": source_tree_sha256,
        "source_hashes": source_hashes,
        "source_npz_schema": npz_schema,
        "official_verifier_sha256": EXPECTED["verifier.py"],
        "official_kickmix_sha256": EXPECTED["kickmix.so"],
        "public_circuit_inputs_read": False,
    }
    write_json(OUT / "source_audit.json", source_audit)

    builder = PACKAGE_COPY / "rebuild.py"
    build_start, argv = time.monotonic(), sys.argv[:]
    sys.argv = [str(builder), "--submission", str(PACKAGE_COPY / "submission.npz"), "--output", str(BUILD_OUT), "--source-output", str(SOURCE_OUT)]
    try:
        with (OUT / "build.stdout").open("w") as stdout, (OUT / "build.stderr").open("w") as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                runpy.run_path(str(builder), run_name="__main__")
    finally:
        sys.argv = argv
    build_seconds = time.monotonic() - build_start

    circuits = {}
    for k, item in enumerate(manifest["loaders"]):
        name = f"angle_k_{k}.kmb"
        circuit = BUILD_OUT / name
        digest = sha256(circuit)
        if digest != item["sha256"]:
            raise RuntimeError(f"source-built circuit hash mismatch: {name}")
        shutil.copyfile(circuit, OUT / name)
        circuits[name] = digest
    if blocked_reads:
        raise RuntimeError(f"blocked public circuit read attempts: {blocked_reads}")

    spec = importlib.util.spec_from_file_location("official_dfthcsos_verify", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the official dfthcsos verifier")
    official = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = official
    spec.loader.exec_module(official)
    verify_start = time.monotonic()
    with (OUT / "verify.stderr").open("w") as stderr:
        with contextlib.redirect_stderr(stderr):
            verification = official.verify(str(OUT))
    verify_seconds = time.monotonic() - verify_start
    if verification.get("status") != "PASS" or blocked_reads:
        raise RuntimeError(f"official verification failed: {verification}")

    write_json(OUT / "verify.json", verification)
    result = {
        "experiment": "exp-064",
        "status": "SOURCE_BUILD_AND_OFFICIAL_VERIFIER_PASS",
        "source_tree_sha256": source_tree_sha256,
        "compiled_circuit_inputs_read": False,
        "blocked_public_circuit_read_attempts": len(blocked_reads),
        "generated_circuit_sha256": circuits,
        "build_seconds": build_seconds,
        "verification_seconds": verify_seconds,
        "official_verification": verification,
    }
    write_json(OUT / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True, default=lambda x: x.item()))


if __name__ == "__main__":
    main()
