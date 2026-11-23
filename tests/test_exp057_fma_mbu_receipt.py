import json
from pathlib import Path
import unittest


RECEIPT = (
    Path(__file__).parents[1]
    / "evals"
    / "2026-11-23-exp057-fma-pair-update-mbu-v18.json"
)


class FmaMbuReceiptTests(unittest.TestCase):
    def test_repeated_component_cost_is_below_gate_but_not_a_candidate(self):
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cost = receipt["cost_audit"]
        self.assertEqual(receipt["checks"]["cases"], 64)
        self.assertEqual(receipt["checks"]["output_errors"], 0)
        self.assertEqual(receipt["checks"]["phase_flips"], 0)
        self.assertEqual(receipt["resources"]["toffoli_like_gates"], 54)
        self.assertEqual(
            cost["fma_pair_updates"] * receipt["resources"]["toffoli_like_gates"],
            cost["repeated_cell_toffoli_like_gates"],
        )
        self.assertLess(
            cost["existing_projected_full_dqi_toffoli_like_gates"],
            cost["full_dqi_toffoli_gate"],
        )
        self.assertEqual(
            cost["existing_projected_full_dqi_toffoli_like_gates"]
            - cost["repeated_cell_toffoli_like_gates"],
            cost["other_costs_in_existing_projection"],
        )
        self.assertAlmostEqual(
            cost["full_dqi_toffoli_gate"]
            - cost["existing_projected_full_dqi_toffoli_like_gates"],
            cost["projected_margin_to_full_dqi_gate"],
        )
        self.assertIsNone(receipt["competition_submission"])
        self.assertEqual(receipt["official_verifier"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
