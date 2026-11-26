"""Build a private Kaggle kernel for the full 70-point FMA resource gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "experiments" / "exp-053" / "inplace_ratio_history.py"
ARITHMETIC = ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
EXPECTED_HISTORY_SHA256 = "00443f971f0b41f5ebe2fb6414168f5cc51affe3ca6514800ff13995e2bb0bf1"
EXPECTED_ARITHMETIC_SHA256 = "c1b8b2ff583ffd5997856605c35d37f7116aa5811e52a3ce04a1ae7215d381c3"
ENTRYPOINT = 'if __name__ == "__main__":'

RANK_ORDER = '''def xor_rank_order(builder, rank1, step, target):
    """Toggle target iff rank1 <= step, using a clean prefix-equality ladder."""
    width = len(rank1)
    if not 0 <= step < (1 << width):
        raise ValueError("rank comparison constant does not fit the register")
    flags = builder.alloc_qubits(width + 1)
    builder.x(flags[0])
    for index, bit in enumerate(reversed(range(width))):
        is_one = (step >> bit) & 1
        control = rank1[bit]
        if not is_one:
            builder.x(control)
        builder.init_and(flags[index], control, flags[index + 1])
        if not is_one:
            builder.x(control)
        if is_one:
            builder.x(control)
            builder.ccx(flags[index], control, target)
            builder.x(control)
    builder.cx(flags[-1], target)
    for index, bit in reversed(list(enumerate(reversed(range(width))))):
        if not ((step >> bit) & 1):
            builder.x(rank1[bit])
        builder.del_and(flags[index], rank1[bit], flags[index + 1])
        if not ((step >> bit) & 1):
            builder.x(rank1[bit])
    builder.x(flags[0])
    builder.free(flags)


'''


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"expected one {label} marker in the pinned source")
    return source.replace(old, new, 1)


def build(out_dir: Path) -> dict:
    if out_dir.exists():
        raise FileExistsError(f"staging directory already exists: {out_dir}")
    history_sha256 = sha256(HISTORY)
    arithmetic_sha256 = sha256(ARITHMETIC)
    if history_sha256 != EXPECTED_HISTORY_SHA256:
        raise ValueError(f"exp-053 source changed: {history_sha256}")
    if arithmetic_sha256 != EXPECTED_ARITHMETIC_SHA256:
        raise ValueError(f"field helper changed: {arithmetic_sha256}")

    source = HISTORY.read_text(encoding="utf-8")
    start = source.index("def xor_rank_order(")
    end = source.index("def append_branch_bit(", start)
    source = source[:start] + RANK_ORDER + source[end:]
    source = replace_once(
        source,
        '    if len(POINTS) > 5:\n'
        '        raise ValueError("the compiled prefix encoder supports at most five pivots")\n',
        "",
        "five-pivot build cap",
    )
    source = replace_once(
        source,
        "        if not 1 <= point_count <= 5:\n"
        '            raise ValueError("point_count must be between 1 and 5")\n',
        "        if not 1 <= point_count <= 70:\n"
        '            raise ValueError("point_count must be between 1 and 70")\n',
        "five-pivot screen cap",
    )
    source = replace_once(
        source,
        ENTRYPOINT,
        "def run_full_recurrence_screen():\n"
        "    result = screen_inplace_prefix_encoder(\n"
        "        case_count=32, measurement_recycle=True, point_count=70\n"
        "    )\n"
        "    return {\n"
        '        "experiment": "exp080-full-70-point-fma-recurrence",\n'
        '        "scope": "Full sample-to-ratio/history map; not the complete DQI decoder.",\n'
        '        "result": result,\n'
        "    }\n\n"
        + ENTRYPOINT,
        "module entrypoint",
    )

    arithmetic = ARITHMETIC.read_text(encoding="utf-8")
    setup = (
        "\n\n# Embedded Apache-2.0 field arithmetic helper from the attributed source kit.\n"
        "km = importlib.import_module('kickmix.kickmix')\n"
        "sys.modules.setdefault('circ', km)\n"
        "import types\n"
        "_arithmetic = types.ModuleType('dqi_inplace_ratio_arithmetic')\n"
        f"exec({arithmetic!r}, _arithmetic.__dict__)\n"
        "sys.modules['dqi_inplace_ratio_arithmetic'] = _arithmetic\n\n"
    )
    script = (
        source.split(ENTRYPOINT, 1)[0].rstrip()
        + setup
        + ENTRYPOINT
        + "\n    print(json.dumps(run_full_recurrence_screen(), indent=2, sort_keys=True))\n"
    )
    metadata = {
        "id": "accelra/exp080-full-70-point-fma-recurrence",
        "title": "exp080 full 70-point FMA recurrence",
        "code_file": "exp080-full-fma-recurrence.py",
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
    code_path = out_dir / metadata["code_file"]
    code_path.write_text(script, encoding="utf-8", newline="\n")
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    manifest = {
        "experiment": "exp080-full-70-point-fma-recurrence",
        "history_source": "experiments/exp-053/inplace_ratio_history.py",
        "history_source_sha256": history_sha256,
        "arithmetic_source": "src/dqi/pro_q2_897/exp/arithmetic/field.py",
        "arithmetic_source_sha256": arithmetic_sha256,
        "generated_kernel_source_sha256": sha256(code_path),
        "generated_kernel_source_bytes": code_path.stat().st_size,
        "point_count": 70,
        "cases": 32,
        "entrypoint": "run_full_recurrence_screen",
    }
    (out_dir / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


if __name__ == "__main__":
    target = ROOT / "kaggle" / "staging" / "exp080-full-fma-recurrence"
    print(json.dumps(build(target), indent=2))
