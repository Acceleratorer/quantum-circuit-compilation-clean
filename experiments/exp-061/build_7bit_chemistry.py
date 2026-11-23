"""Regenerate ThemBones' 7-bit chemistry loaders from the numeric fit only.

The input factorization is Apache-2.0 data from
danishlynxthembones/vqcc-thembones-milestone-set. This script reads only its
submission.npz; all ANGLE_k circuits are built by this repository's qrom code.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from angleload import build_family, circuit_stats, write_family  # noqa: E402


SOURCE_DATASET = "danishlynxthembones/vqcc-thembones-milestone-set"
SOURCE_URL = f"https://www.kaggle.com/datasets/{SOURCE_DATASET}"
SOURCE_NPZ = Path(__file__).parent / "external" / "thembones-milestone" / "set" / "dfthcsos" / "submission.npz"
SOURCE_SHA256 = "e05fb18f808e410ff126d68b8415e6fd4b33712760f35f90412e96ba6a331f73"
OUTPUT = Path(__file__).parent / "out" / "chemistry-7bit-source-build"
REPORT = Path(__file__).parent / "out" / "chemistry-7bit-build-report.json"
EXPECTED_ANGLE_WORDS_SHAPE = (1219, 75)
EXPECTED_BROT = 7
EXPECTED_BATCH_SIZE = 5
EXPECTED_STATIC_T_PER_PASS = 3468


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha256(SOURCE_NPZ) != SOURCE_SHA256:
        raise SystemExit("The pinned Apache-2.0 factorization is missing or changed.")
    if OUTPUT.exists() or REPORT.exists():
        raise SystemExit("Refusing to overwrite an existing exp-061 output.")

    with np.load(SOURCE_NPZ, allow_pickle=False) as archive:
        words = np.asarray(archive["angle_words"], dtype=np.int64)
        fit_shape = list(archive["U"].shape)
    if words.shape != EXPECTED_ANGLE_WORDS_SHAPE:
        raise SystemExit(f"Unexpected angle_words shape: {words.shape}")
    if words.size == 0 or words.min() < 0 or words.max() >= (1 << EXPECTED_BROT):
        raise SystemExit("The input angle words do not fit the declared 7-bit width.")

    circuits = build_family(words, brot=EXPECTED_BROT, J=EXPECTED_BATCH_SIZE)
    stats = circuit_stats(circuits)
    total_static_t = sum(row["toffoli_static"] for row in stats)
    if total_static_t != EXPECTED_STATIC_T_PER_PASS:
        raise SystemExit(f"ANGLE_k static count {total_static_t} != {EXPECTED_STATIC_T_PER_PASS}")

    OUTPUT.mkdir(parents=True)
    paths = write_family(circuits, OUTPUT, fmt="kmb")
    shutil.copyfile(SOURCE_NPZ, OUTPUT / "submission.npz")
    report = {
        "experiment": "exp-061-7bit-source-generated-chemistry-loaders",
        "source_dataset": SOURCE_DATASET,
        "source_url": SOURCE_URL,
        "source_license": "Apache-2.0",
        "source_npz_sha256": SOURCE_SHA256,
        "source_npz_is_compiled_circuit": False,
        "copied_or_read_compiled_circuit": False,
        "fit_shape_U": fit_shape,
        "angle_words_shape": list(words.shape),
        "brot": EXPECTED_BROT,
        "batch_size": EXPECTED_BATCH_SIZE,
        "num_angle_circuits": len(paths),
        "static_t_per_pass": total_static_t,
        "circuits": [
            {**row, "sha256": sha256(path)} for row, path in zip(stats, paths, strict=True)
        ],
        "output_dir": str(OUTPUT.relative_to(ROOT)),
        "generator": "src/angleload/qrom.py",
        "official_verifier": "not run by this builder",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(paths)} source-generated loaders; {total_static_t:,} static T per pass.")
    print(f"Output: {OUTPUT}")
    print(f"Receipt: {REPORT}")


if __name__ == "__main__":
    main()
