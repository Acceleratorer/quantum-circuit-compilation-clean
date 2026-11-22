import importlib.util
from pathlib import Path
from random import Random
import sys
import unittest


MODULE_PATH = (
    Path(__file__).parents[1]
    / "experiments"
    / "exp-057"
    / "streaming_fixed_shape_decoder.py"
)
SPEC = importlib.util.spec_from_file_location("exp057_streaming_decoder", MODULE_PATH)
decoder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = decoder
SPEC.loader.exec_module(decoder)

KERNEL_PATH = (
    Path(__file__).parents[1]
    / "experiments"
    / "exp-057"
    / "streaming_prefix_kernel.py"
)
KERNEL_SPEC = importlib.util.spec_from_file_location(
    "exp057_streaming_prefix_kernel", KERNEL_PATH
)
kernel = importlib.util.module_from_spec(KERNEL_SPEC)
assert KERNEL_SPEC.loader is not None
sys.modules[KERNEL_SPEC.name] = kernel
KERNEL_SPEC.loader.exec_module(kernel)

sys.path.insert(0, str(Path(__file__).parents[1] / "experiments" / "exp-049"))
import fma_state_compression as fma


class TestField:
    def mul(self, left, right):
        return fma.gf_mul(left, right, 0x1053, 12)

    def invert(self, value):
        return fma.gf_inv(value, 0x1053, 12)


class TailTransitionTests(unittest.TestCase):
    def test_tail_transition_is_invertible_for_every_supported_gf8_prefix(self):
        result = decoder.screen_gf8_tail_transition()
        self.assertEqual(result["supported_prefixes"], 2016)
        self.assertEqual(result["prefix_annihilation_errors"], 0)
        self.assertEqual(result["tail_round_trip_checks"], 2016 * 4)
        self.assertEqual(result["tail_round_trip_errors"], 0)
        self.assertEqual(result["first_row_zero_slopes"], 700)
        self.assertEqual(result["alternate_row_zero_errors"], 0)
        self.assertEqual(result["bezout_complementary_rows"], 2016)
        self.assertEqual(result["distinct_tail_matrices"], 444)
        self.assertEqual(result["matrix_only_collisions"], 1572)
        self.assertEqual(result["maximum_coefficients_per_tail_matrix"], 7)
        self.assertEqual(result["minimum_b1_discriminator_bits"], 3)
        self.assertEqual(result["matrix_and_b1_collisions"], 0)
        self.assertEqual(result["b1_discriminator_reconstruction_errors"], 0)
        self.assertEqual(result["matrix_recurrence_checks"], 2016 * 4)
        self.assertEqual(result["matrix_recurrence_errors"], 0)
        self.assertEqual(result["tail_points"], {"start": 4, "end": 7, "count": 4})
        self.assertEqual(result["result"], "PASS")

    def test_tail_transition_matches_seeded_gf12_verifier_samples(self):
        result = decoder.screen_gf12_verifier_tail_transition()
        self.assertEqual(result["verifier_form_samples"], 32)
        self.assertEqual(result["pivot_counts"], {"a0": 32, "a1": 0})
        self.assertEqual(result["prefix_annihilation_errors"], 0)
        self.assertEqual(result["tail_round_trip_checks"], 32 * 66)
        self.assertEqual(result["tail_round_trip_errors"], 0)
        self.assertEqual(result["first_row_zero_slopes"], 1)
        self.assertEqual(result["alternate_row_zero_errors"], 0)
        self.assertEqual(result["bezout_complementary_rows"], 32)
        self.assertEqual(result["matrix_b1_reconstruction_errors"], 0)
        self.assertEqual(result["matrix_recurrence_checks"], 32 * 66)
        self.assertEqual(result["matrix_recurrence_errors"], 0)
        self.assertEqual(result["tail_points"], {"start": 4, "end": 69, "count": 66})
        self.assertEqual(result["result"], "PASS")


class VerifierFormPrefixTests(unittest.TestCase):
    def test_syndrome_to_fma_map_matches_reference(self):
        field = TestField()
        rng = Random(0xA660516)
        locations = rng.sample(range(1, 1 << 12), 31)
        magnitudes = [rng.randrange(1, 1 << 12) for _ in locations]
        syndrome = [0] * 70
        for location, magnitude in zip(locations, magnitudes):
            power = location
            for index in range(70):
                syndrome[index] ^= field.mul(magnitude, power)
                power = field.mul(power, location)

        actual = kernel.syndrome_to_fma_samples(syndrome, field)
        expected = fma.syndrome_to_fma_samples(
            syndrome, range(70), field.mul
        )
        self.assertEqual(actual, tuple(expected))

    def test_generated_cases_reconstruct_the_supported_prefix(self):
        field = TestField()
        cases = kernel.generate_verifier_form_cases(field, 8, seed=0xA660517)
        self.assertEqual(len(cases), 8)
        for case in cases:
            self.assertTrue(29 <= case["weight"] <= 35)
            self.assertTrue(
                kernel.coefficients_have_supported_shape(
                    case["coefficients"], field
                )
            )
            self.assertEqual(
                kernel.coefficients_from_four_samples(case["samples"][:4], field),
                case["coefficients"],
            )
            coefficients, pivot = kernel.coefficients_from_prefix_classical(
                *case["prefix_state"], field
            )
            self.assertEqual(coefficients, case["coefficients"])
            self.assertEqual(pivot, case["pivot"])
