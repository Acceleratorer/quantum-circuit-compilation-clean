from random import Random
import sys
from pathlib import Path
import unittest

import numpy as np
import kickmix as km


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "exp-057"))
import phase_compatibility

sys.modules["circ"] = km
KERNEL_ROOT = ROOT / "src" / "dqi" / "pro_q2_897"
sys.path.insert(0, str(KERNEL_ROOT))
sys.path.insert(0, str(KERNEL_ROOT / "exp" / "arithmetic"))
from exp.mul99.phase36 import phase_inverse36_pivot


def bit_columns(values):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack([((values >> bit) & 1).astype(np.bool_) for bit in range(12)])


class PhaseCompatibilityTests(unittest.TestCase):
    def test_forney_values_reproduce_verifier_mbuc_phase(self):
        result = phase_compatibility.run_screen()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["cases"], 32)
        self.assertEqual(result["weights"], {31: 16, 35: 16})
        self.assertEqual(result["forced_fma_prefix_roots"], [1, 2, 3])
        self.assertEqual(result["recovered_error_values"], 32 * 33)
        self.assertEqual(result["value_mismatches"], 0)
        self.assertEqual(result["phase_mismatches"], 0)
        self.assertEqual(result["residue_identity_errors"], 0)
        self.assertEqual(result["aggregate_phase_mismatches"], 0)

    def test_existing_inverse_phase_helper_costs_36_t_per_mask(self):
        builder = km.CircuitBuilder()
        value = builder.alloc_qubits(12)
        mask = builder.alloc_bits(12)
        phase_inverse36_pivot(builder, value, mask)
        circuit = builder.finish_circuit()

        rng = Random(0xA66061)
        count = 64
        values = np.asarray([rng.randrange(1 << 12) for _ in range(count)])
        masks = np.asarray([rng.randrange(1 << 12) for _ in range(count)])
        simulator = km.Simulator(
            batch_size=count,
            debug_print=False,
            counting_operations=True,
            seed=0,
        )
        simulator.use_same_registers_as(circuit)
        simulator.write_across_shots(value, bit_columns(values))
        simulator.write_across_shots(mask, bit_columns(masks))
        simulator.do(circuit)

        expected_phase = np.asarray(
            [
                (
                    phase_compatibility.fma.gf_inv(
                        int(v), phase_compatibility.MODULUS, 12
                    )
                    & int(m)
                ).bit_count()
                & 1
                for v, m in zip(values, masks)
            ],
            dtype=np.bool_,
        )
        self.assertTrue(
            np.array_equal(simulator.read_phase_flipped_across_shots(), expected_phase)
        )
        self.assertEqual(circuit.num_qubits, 24)
        self.assertEqual(circuit.operation_statistics().num_toffoli_like, 168)
        self.assertEqual(simulator.operation_statistics().num_toffoli_like, 36 * count)
        self.assertTrue(np.array_equal(simulator.read_across_shots(value), bit_columns(values)))
        scratch = [km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in value]
        self.assertFalse(np.any(simulator.read_across_shots(km.array(scratch))))


if __name__ == "__main__":
    unittest.main()
