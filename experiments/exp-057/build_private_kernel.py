"""Bundle the exp-057 gate screen for a private Kaggle kernel."""

from __future__ import annotations

import argparse
import base64
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("streaming_prefix_kernel.py")
ARITHMETIC = ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
HELPER_ROOT = ROOT / "src" / "dqi" / "pro_q2_897"
NOTICE = ROOT / "src" / "dqi" / "NOTICE"
LICENSE = ROOT / "src" / "dqi" / "LICENSE"
ENTRYPOINT = 'if __name__ == "__main__":'


def helper_archive() -> str:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((HELPER_ROOT / "exp").rglob("*")):
            if path.is_file() and path.suffix in {".py", ".json"}:
                archive.write(path, Path("exp") / path.relative_to(HELPER_ROOT / "exp"))
        archive.write(NOTICE, "NOTICE")
        archive.write(LICENSE, "LICENSE")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def build(out_dir: Path, screen: str = "all") -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(ENTRYPOINT) != 1:
        raise ValueError("expected one module entrypoint")
    body, main = source.split(ENTRYPOINT, 1)
    if screen == "phase-node-alignment":
        main = (
            "\n    print(json.dumps(\n"
            "        run_fma_phase_node_alignment_screen(), indent=2, sort_keys=True\n"
            "    ))\n"
        )
    elif screen == "phase-node-alignment-no-convert":
        main = (
            "\n    print(json.dumps(\n"
            "        run_fma_phase_node_alignment_screen(use_converter=False),\n"
            "        indent=2, sort_keys=True\n"
            "    ))\n"
        )
    arithmetic = ARITHMETIC.read_text(encoding="utf-8")
    setup = (
        "\n\n# Embedded unchanged Apache-2.0 gate arithmetic helper.\n"
        "km = importlib.import_module('kickmix.kickmix')\n"
        "sys.modules.setdefault('circ', km)\n"
        "import types\n"
        "_arithmetic = types.ModuleType('dqi_streaming_prefix_arithmetic')\n"
        f"exec({arithmetic!r}, _arithmetic.__dict__)\n"
        "ARITHMETIC = _arithmetic\n\n"
    )
    helpers = (
        "# Embedded helper source archive; Apache-2.0 attribution is in NOTICE.\n"
        f"HELPER_ARCHIVE_B64 = {helper_archive()!r}\n\n"
    )
    script = body.rstrip() + setup + helpers + ENTRYPOINT + main
    metadata = {
        "id": "accelra/exp057-streaming-prefix-state",
        "title": "exp057 streaming prefix state",
        "code_file": "exp057-streaming-prefix-state.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": True,
        "keywords": [],
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": ["google-verifiable-quantum-circuit-compilation"],
        "model_sources": [],
    }
    out_dir.mkdir(parents=True, exist_ok=False)
    (out_dir / metadata["code_file"]).write_text(script, encoding="utf-8", newline="\n")
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"script_bytes": len(script.encode("utf-8")), "output": str(out_dir)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path, help="new project-local Kaggle staging directory")
    parser.add_argument(
        "--screen",
        choices=(
            "all",
            "phase-node-alignment",
            "phase-node-alignment-no-convert",
        ),
        default="all",
        help="run the full gate suite or only the FMA phase bridge screen",
    )
    args = parser.parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    build(out_dir.resolve(), screen=args.screen)


if __name__ == "__main__":
    main()
