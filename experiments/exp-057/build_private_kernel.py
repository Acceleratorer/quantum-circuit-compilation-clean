"""Bundle the exp-057 gate screen for a private Kaggle kernel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("streaming_prefix_kernel.py")
ARITHMETIC = ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
ENTRYPOINT = 'if __name__ == "__main__":'


def build(out_dir: Path) -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(ENTRYPOINT) != 1:
        raise ValueError("expected one module entrypoint")
    body, main = source.split(ENTRYPOINT, 1)
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
    script = body.rstrip() + setup + ENTRYPOINT + main
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
    args = parser.parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    build(out_dir.resolve())


if __name__ == "__main__":
    main()
