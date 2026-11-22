import importlib.util
from pathlib import Path
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
