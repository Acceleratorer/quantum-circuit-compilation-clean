"""Count the forward and reverse CONVERT costs used by exp-057 v19."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

import kickmix as km


ROOT = Path(__file__).resolve().parents[2]
DQI = ROOT / "src" / "dqi" / "pro_q2_897"
sys.modules.setdefault("circ", km)
sys.modules.setdefault("kickmix.kickmix", km)
sys.path[:0] = [str(ROOT / "src"), str(DQI)]

from exp.convert_short_hankel.phase34 import convert_safe  # noqa: E402
from kmx_tag_count import count  # noqa: E402


def run():
    builder = km.CircuitBuilder()
    numerator = [builder.alloc_qubits(12) for _ in range(35)]
    denominator = [builder.alloc_qubits(12) for _ in range(35)]

    with builder.mark("convert_forward"):
        token = convert_safe(builder, numerator, denominator, monic_root=True)
    with builder.mark("convert_reverse"):
        convert_safe(builder, numerator, denominator, True, phase_token=token)

    circuit = builder.finish_circuit()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "convert.kmx"
        circuit.to_file(str(path), format="kmx")
        tagged = count(str(path))["by_path"]

    stages = {"convert_forward": 0, "convert_reverse": 0}
    for path, gates in tagged.items():
        stage = path.split("/", 1)[0]
        if stage in stages:
            stages[stage] += gates
    return {
        "qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "stage_toffoli_like_gates": stages,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
