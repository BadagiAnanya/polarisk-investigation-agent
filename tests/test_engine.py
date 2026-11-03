import tempfile
import unittest
from pathlib import Path

from investigator.data import seed_database
from investigator.engine import evaluate, investigate


class InvestigationEngineTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temporary_directory.name) / "demo.db"
        seed_database(self.db_path)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_structuring_case_has_exact_evidence(self):
        packet = investigate("ALERT-STRUCT-001", self.db_path)
        self.assertEqual(packet["suspected_typology"], "structuring")
        self.assertTrue(packet["evidence_verification"]["passed"])
        self.assertEqual(len(packet["evidence"]), 5)

    def test_legitimate_salary_is_not_marked_suspicious(self):
        packet = investigate("ALERT-SALARY-001", self.db_path)
        self.assertEqual(packet["suspected_typology"], "insufficient_evidence")
        self.assertTrue(packet["requires_human_review"])

    def test_evaluation_regression_suite_passes(self):
        report = evaluate(self.db_path)
        self.assertEqual(report["summary"]["typology_accuracy"], 1.0)
        self.assertTrue(report["summary"]["all_evidence_verified"])


if __name__ == "__main__":
    unittest.main()
