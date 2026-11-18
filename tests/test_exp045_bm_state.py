from itertools import product
from pathlib import Path
import importlib.util
import random
import sys
import unittest


MODULE_PATH = Path(__file__).parents[1] / "experiments" / "exp-045" / "bm_state_model.py"
SPEC = importlib.util.spec_from_file_location("exp045_bm_state_model", MODULE_PATH)
bm_model = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = bm_model
SPEC.loader.exec_module(bm_model)


def _check_all_prefix_states_are_injective(test_case, field, max_length):
    for length in range(max_length + 1):
        seen = set()
        for sequence in product(range(field.order), repeat=length):
            state = bm_model.bm_prefix_states(sequence, field)[-1]
            test_case.assertNotIn(state.key(), seen)
            test_case.assertLessEqual(state.coefficient_words, length)
            seen.add(state.key())
        test_case.assertEqual(len(seen), field.order**length)


class BMStateTests(unittest.TestCase):
    def test_small_binary_fields_have_injective_packed_prefix_states(self):
        _check_all_prefix_states_are_injective(self, bm_model.GF2Field(1, 0b11), 12)
        _check_all_prefix_states_are_injective(self, bm_model.GF2Field(2, 0b111), 7)
        _check_all_prefix_states_are_injective(self, bm_model.GF2Field(3, 0b1011), 6)

    def test_gf2_12_prefix_degree_bound_on_seeded_sequences(self):
        field = bm_model.GF2Field(12, 0x1053)
        rng = random.Random(20261118)
        max_state_bits = 0
        max_coefficient_words = 0

        for _ in range(128):
            sequence = [rng.randrange(field.order) for _ in range(70)]
            states = bm_model.bm_prefix_states(sequence, field)
            self.assertLessEqual(max(state.coefficient_words - k for k, state in enumerate(states)), 0)

            for k, state in enumerate(states):
                self.assertEqual(state.linear_complexity, state.c_degree)
                max_coefficient_words = max(max_coefficient_words, state.coefficient_words)
                state_bits = field.degree * state.coefficient_words + field.degree + (k + 1).bit_length()
                max_state_bits = max(max_state_bits, state_bits)

        self.assertEqual(max_coefficient_words, 69)
        self.assertEqual(max_state_bits, 847)


if __name__ == "__main__":
    unittest.main()
