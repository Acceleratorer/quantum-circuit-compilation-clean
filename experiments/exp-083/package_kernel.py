"""Bundle the reviewed source builders into Kaggle's single-file kernel script."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import textwrap
import zipfile


ROOT = Path(__file__).resolve().parent
SOURCES = {
    "source/exp062_rebuild_verify.py": ROOT.parent / "exp-062" / "kernel" / "rebuild_verify.py",
    "source/exp063_rebuild_verify.py": ROOT.parent / "exp-063" / "kernel" / "rebuild_verify.py",
    "source/exp064_rebuild_verify.py": ROOT.parent / "exp-064" / "kernel" / "rebuild_verify.py",
    "source/v20_build_chemistry.py": ROOT / "module" / "v20_build_chemistry.py",
    "source/payload/chemistry_weights.b85": ROOT.parent / "exp-074" / "module" / "payload" / "chemistry_weights.b85",
    "source/payload/v20_loader_programs.b85": ROOT.parent / "exp-074" / "module" / "payload" / "v20_loader_programs.b85",
}
MARKER_START = "# BEGIN GENERATED SOURCE BUNDLE"
MARKER_END = "# END GENERATED SOURCE BUNDLE"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="new staging directory outside exp-083")
    output = parser.parse_args().output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("The bundle output must be outside the exp-083 directory")
    if output.exists() and any(output.iterdir()):
        parser.error(f"Choose an empty output directory: {output}")
    missing = [str(path) for path in SOURCES.values() if not path.is_file()]
    if missing:
        parser.error(f"Reviewed source file missing: {missing[0]}")

    manifest = {name: sha256(path.read_bytes()) for name, path in sorted(SOURCES.items())}
    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(SOURCES.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    payload = archive_data.getvalue()
    encoded = textwrap.wrap(base64.b85encode(payload).decode("ascii"), width=100)
    generated = [
        f"BUNDLE_SHA256 = {sha256(payload)!r}",
        f"BUNDLE_MANIFEST = {json.dumps(manifest, sort_keys=True)}",
        "BUNDLE_B85 = (",
        *(f"    {line!r}" for line in encoded),
        ")",
    ]
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    if source.count(MARKER_START) != 1 or source.count(MARKER_END) != 1:
        parser.error("Source bundle marker must appear exactly once")
    start = source.index(MARKER_START)
    end = source.index(MARKER_END, start) + len(MARKER_END)
    replacement = "\n".join([MARKER_START, *generated, MARKER_END])
    bundled_source = source[:start] + replacement + source[end:]

    output.mkdir(parents=True, exist_ok=True)
    (output / "main.py").write_text(bundled_source, encoding="utf-8", newline="\n")
    metadata = json.loads((ROOT / "kernel-metadata.json").read_text(encoding="utf-8"))
    (output / "kernel-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "staging_dir": str(output),
                "source_bundle_sha256": sha256(payload),
                "source_files": manifest,
                "main_py_bytes": (output / "main.py").stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
