"""Create a self-contained private Kaggle kernel script outside the checkout."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import textwrap
import zipfile


EXPERIMENT = Path(__file__).resolve().parent
REPOSITORY = EXPERIMENT.parents[1]
SOURCE_ROOT = REPOSITORY / "src" / "dqi"
IMPORT_MARKER = 'SOURCE_BUNDLE_B85 = ""'
HASH_MARKER = 'SOURCE_BUNDLE_SHA256 = ""'
MANIFEST_MARKER = 'EXPECTED_MANIFEST_SHA256 = ""'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="new empty staging directory outside the Git checkout")
    output = parser.parse_args().output_dir.resolve()
    if output == REPOSITORY or REPOSITORY in output.parents:
        parser.error("staging output must be outside the Git checkout")
    if output.exists() and any(output.iterdir()):
        parser.error(f"choose an empty staging directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    manifest_bytes = (SOURCE_ROOT / "MANIFEST.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    members = ["generate.py", "MANIFEST.json", "LICENSE", "NOTICE"]
    members.extend(f"{manifest['kit_dir']}/{name}" for name in manifest["files"])
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            member = PurePosixPath(name)
            if member.is_absolute() or ".." in member.parts or "\\" in name:
                raise RuntimeError(f"unsafe source path: {name}")
            path = SOURCE_ROOT.joinpath(*member.parts)
            if not path.is_file():
                raise RuntimeError(f"missing source file: {path}")
            if name.startswith(f"{manifest['kit_dir']}/"):
                relative = name.split("/", 1)[1]
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != manifest["files"][relative]:
                    raise RuntimeError(f"source manifest mismatch: {name}")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    archive_bytes = archive_buffer.getvalue()
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    encoded = base64.b85encode(archive_bytes).decode("ascii")
    literals = "\n".join(f"    {line!r}" for line in textwrap.wrap(encoded, width=100))
    source = (EXPERIMENT / "main.py").read_text(encoding="utf-8")
    if source.count(IMPORT_MARKER) != 1 or source.count(HASH_MARKER) != 1 or source.count(MANIFEST_MARKER) != 1:
        raise RuntimeError("expected one source-bundle marker of each kind")
    source = source.replace(IMPORT_MARKER, f'SOURCE_BUNDLE_B85 = (\n{literals}\n)')
    source = source.replace(HASH_MARKER, f'SOURCE_BUNDLE_SHA256 = "{archive_sha256}"')
    source = source.replace(MANIFEST_MARKER, f'EXPECTED_MANIFEST_SHA256 = "{manifest_sha256}"')
    main_path = output / "main.py"
    main_path.write_text(source, encoding="utf-8", newline="\n")
    metadata = json.loads((EXPERIMENT / "kernel-metadata.json").read_text(encoding="utf-8"))
    (output / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "staging_dir": str(output),
        "script_bytes": main_path.stat().st_size,
        "script_sha256": hashlib.sha256(main_path.read_bytes()).hexdigest(),
        "source_bundle_bytes": len(archive_bytes),
        "source_bundle_sha256": archive_sha256,
        "source_manifest_sha256": manifest_sha256,
        "source_files": len(manifest["files"]),
    }, indent=2))


if __name__ == "__main__":
    main()
