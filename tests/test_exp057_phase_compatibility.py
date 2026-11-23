import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "exp-057"))
import phase_compatibility


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


if __name__ == "__main__":
    unittest.main()
