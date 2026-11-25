"""Create Kaggle's single-file script bundle from the separated experiment sources."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
from pathlib import Path
import textwrap
import zipfile


ROOT = Path(__file__).resolve().parent
IMPORT_BLOCK = '''sys.path.insert(0, str(Path(__file__).resolve().parent / "module"))
from build_chemistry import build_chemistry'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="new directory outside the Git checkout")
    output = parser.parse_args().output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("The bundle output must be outside the experiment checkout")
    if output.exists() and any(output.iterdir()):
        parser.error(f"Choose an empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in (
            Path("module/build_chemistry.py"),
            Path("module/payload/chemistry_weights.b85"),
            Path("module/payload/loader_programs.b85"),
        ):
            archive.write(ROOT / relative, relative.as_posix())
    encoded = base64.b85encode(archive_data.getvalue()).decode("ascii")
    chunks = textwrap.wrap(encoded, width=100)
    literals = "\n".join(f"    {chunk!r}" for chunk in chunks)
    bundle_import = f'''import base64 as _base64
import io as _io
import zipfile as _zipfile

_source_root = Path("/kaggle/working/exp072-source")
if _source_root.exists():
    raise RuntimeError(f"Refusing to reuse source bundle directory: {{_source_root}}")
_source_root.mkdir(parents=True)
_source_archive = _base64.b85decode(
    (
{literals}
    )
)
with _zipfile.ZipFile(_io.BytesIO(_source_archive)) as _archive:
    _archive.extractall(_source_root)
sys.path.insert(0, str(_source_root / "module"))
from build_chemistry import build_chemistry'''

    source = (ROOT / "main.py").read_text(encoding="utf-8")
    if source.count(IMPORT_BLOCK) != 1:
        raise RuntimeError("The source import block changed; update the packager deliberately")
    bundled_source = source.replace(IMPORT_BLOCK, bundle_import)
    metadata = (ROOT / "kernel-metadata.json").read_text(encoding="utf-8")
    (output / "main.py").write_text(bundled_source, encoding="utf-8", newline="\n")
    (output / "kernel-metadata.json").write_text(metadata, encoding="utf-8", newline="\n")
    print(
        f"bundle={output}\n"
        f"script_bytes={(output / 'main.py').stat().st_size}\n"
        f"script_sha256={hashlib.sha256((output / 'main.py').read_bytes()).hexdigest()}\n"
        f"source_archive_bytes={len(archive_data.getvalue())}"
    )


if __name__ == "__main__":
    main()
