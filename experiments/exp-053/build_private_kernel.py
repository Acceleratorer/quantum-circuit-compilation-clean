"""Build the self-contained source for the private exp-053 Kaggle kernel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().with_name("inplace_ratio_history.py")
ARITHMETIC = ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
ENTRYPOINT = 'if __name__ == "__main__":'


def build(out_dir: Path, entrypoint: str = "run_screen") -> None:
    if entrypoint not in {"run_screen", "run_handoff_screen"}:
        raise ValueError(f"unsupported kernel entrypoint: {entrypoint}")
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(ENTRYPOINT) != 1:
        raise ValueError("expected one module entrypoint")
    body, _main = source.split(ENTRYPOINT, 1)
    arithmetic = ARITHMETIC.read_text(encoding="utf-8")
    setup = (
        "\n\n# Embedded unchanged Apache-2.0 gate arithmetic helper.\n"
        "km = importlib.import_module('kickmix.kickmix')\n"
        "sys.modules.setdefault('circ', km)\n"
        "import types\n"
        "_arithmetic = types.ModuleType('dqi_inplace_ratio_arithmetic')\n"
        f"exec({arithmetic!r}, _arithmetic.__dict__)\n"
        "sys.modules['dqi_inplace_ratio_arithmetic'] = _arithmetic\n\n"
    )
    script = (
        body.rstrip()
        + setup
        + ENTRYPOINT
        + f"\n    print(json.dumps({entrypoint}(), indent=2, sort_keys=True))\n"
    )

    metadata = {
        "id": "accelra/exp053-inplace-ratio-history",
        "title": "exp053 inplace ratio history",
        "code_file": "exp053-inplace-ratio-history.py",
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
    print(
        json.dumps(
            {
                "script_bytes": len(script.encode("utf-8")),
                "arithmetic_bytes": len(arithmetic.encode("utf-8")),
                "output": str(out_dir),
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path, help="new project-local Kaggle staging directory")
    parser.add_argument(
        "--entrypoint",
        choices=("run_screen", "run_handoff_screen"),
        default="run_screen",
    )
    args = parser.parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    build(out_dir.resolve(), args.entrypoint)


if __name__ == "__main__":
    main()
