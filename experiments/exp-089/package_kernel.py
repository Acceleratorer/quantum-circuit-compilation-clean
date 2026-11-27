"""Package the pinned QV2 DQI source into a private Kaggle kernel directory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


EXPERIMENT = Path(__file__).resolve().parent
REPOSITORY = EXPERIMENT.parents[1]
SOURCE_ROOT = REPOSITORY / "src/dqi/qv2_m4"
SOURCE_FILES_MARKER = "EXPECTED_SOURCE_FILES = {}"
MANIFEST_HASH_MARKER = 'SOURCE_MANIFEST_SHA256 = ""'
UPSTREAM_MANIFEST_HASH_MARKER = 'UPSTREAM_GENERATORS_MANIFEST_SHA256 = "623c1127bbfe18083ebab46ad2338444451071ded5c4ed319f64f07f1d265a0a"'
LOCAL_SNAPSHOT_HASH_MARKER = 'LOCAL_DATASET_SNAPSHOT_SHA256 = "9fe082e0d22e3b95b802b0c0ba548c6798ebd869cff503446af2fb82ea11148e"'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_source_files() -> tuple[dict[str, str], dict]:
    manifest = json.loads((SOURCE_ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    root_docs = {"CREDITS.md", "DEPENDENCIES.md", "LICENSE", "NOTICE", "KIT_README.md"}
    pinned = {name: digest for name, digest in expected.items() if name.startswith("kit/") or name in root_docs}
    if len(pinned) != 97:
        raise RuntimeError(f"expected 92 DQI sources and five notices, found {len(pinned)} files")
    for name, digest in pinned.items():
        member = PurePosixPath(name)
        if member.is_absolute() or ".." in member.parts or "\\" in name:
            raise RuntimeError(f"unsafe source path: {name}")
        path = SOURCE_ROOT.joinpath(*member.parts)
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise RuntimeError(f"source manifest mismatch: {name}")
        if path.suffix.lower() in {".kmb", ".kmx", ".npz"}:
            raise RuntimeError(f"compiled circuit file in source manifest: {name}")
    return pinned, manifest["source"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="new empty directory outside the Git checkout")
    output = parser.parse_args().output_dir.resolve()
    if output == REPOSITORY or REPOSITORY in output.parents:
        parser.error("staging output must be outside the Git checkout")
    if output.exists() and any(output.iterdir()):
        parser.error(f"choose an empty staging directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    source_files, provenance = pinned_source_files()
    manifest_bytes = json.dumps(source_files, sort_keys=True, separators=(",", ":")).encode()
    manifest_sha = sha256(manifest_bytes)
    script = (EXPERIMENT / "main.py").read_text(encoding="utf-8")
    markers = (
        SOURCE_FILES_MARKER,
        MANIFEST_HASH_MARKER,
        UPSTREAM_MANIFEST_HASH_MARKER,
        LOCAL_SNAPSHOT_HASH_MARKER,
    )
    if any(script.count(marker) != 1 for marker in markers):
        raise RuntimeError("source manifest placeholder is missing or duplicated")
    source_literal = "EXPECTED_SOURCE_FILES = " + json.dumps(source_files, indent=2, sort_keys=True)
    script = script.replace(SOURCE_FILES_MARKER, source_literal)
    script = script.replace(MANIFEST_HASH_MARKER, f'SOURCE_MANIFEST_SHA256 = "{manifest_sha}"')
    script = script.replace(
        UPSTREAM_MANIFEST_HASH_MARKER,
        f'UPSTREAM_GENERATORS_MANIFEST_SHA256 = "{provenance["upstream_generators_manifest_sha256"]}"',
    )
    script = script.replace(
        LOCAL_SNAPSHOT_HASH_MARKER,
        f'LOCAL_DATASET_SNAPSHOT_SHA256 = "{provenance["local_dataset_snapshot_sha256"]}"',
    )
    main_path = output / "main.py"
    main_path.write_text(script, encoding="utf-8", newline="\n")
    metadata = json.loads((EXPERIMENT / "kernel-metadata.json").read_text(encoding="utf-8"))
    (output / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "staging_dir": str(output),
        "script_bytes": main_path.stat().st_size,
        "script_sha256": sha256(main_path.read_bytes()),
        "source_manifest_sha256": manifest_sha,
        "source_files": len(source_files),
        "upstream_generators_manifest_sha256": provenance["upstream_generators_manifest_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
