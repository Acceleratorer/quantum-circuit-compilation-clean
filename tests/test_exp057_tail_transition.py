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
        self.assertEqual(result["tail_round_trip_errors"], 0)
        self.assertEqual(result["result"], "PASS")

    def test_tail_transition_matches_seeded_gf12_verifier_samples(self):
        result = decoder.screen_gf12_verifier_tail_transition()
        self.assertEqual(result["verifier_form_samples"], 32)
        self.assertEqual(result["pivot_counts"], {"a0": 32, "a1": 0})
        self.assertEqual(result["prefix_annihilation_errors"], 0)
        self.assertEqual(result["tail_round_trip_errors"], 0)
        self.assertEqual(result["result"], "PASS")
