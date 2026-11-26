"""Bundle the tracked DQI generator into a private Kaggle script kernel."""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
from pathlib import Path
import textwrap
import zipfile


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parents[1] / "src" / "dqi"
PLACEHOLDER = 'SOURCE_BUNDLE_B85 = "__SOURCE_BUNDLE_B85__"'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    output = parser.parse_args().output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Bundle output must be outside the experiment folder")
    if output.exists() and any(output.iterdir()):
        parser.error(f"Choose an empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    archive_data = io.BytesIO()
    with zipfile.ZipFile(archive_data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(SOURCE_ROOT.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            archive.write(path, (Path("dqi") / path.relative_to(SOURCE_ROOT)).as_posix())
    encoded = base64.b85encode(archive_data.getvalue()).decode("ascii")
    literals = "\n".join(f"    {chunk!r}" for chunk in textwrap.wrap(encoded, width=100))
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    if source.count(PLACEHOLDER) != 1:
        raise RuntimeError("Expected one source bundle placeholder")
    bundled = source.replace(PLACEHOLDER, f"SOURCE_BUNDLE_B85 = (\n{literals}\n)")
    (output / "main.py").write_text(bundled, encoding="utf-8", newline="\n")
    (output / "kernel-metadata.json").write_bytes((ROOT / "kernel-metadata.json").read_bytes())
    print(
        f"bundle={output}\n"
        f"script_bytes={(output / 'main.py').stat().st_size}\n"
        f"script_sha256={hashlib.sha256((output / 'main.py').read_bytes()).hexdigest()}\n"
        f"source_archive_bytes={len(archive_data.getvalue())}"
    )


if __name__ == "__main__":
    main()
