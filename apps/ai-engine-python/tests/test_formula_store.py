import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.formula_store import FormulaStore


class FormulaStoreTest(unittest.TestCase):
    def test_appends_and_reads_latest_formula_snapshot(self):
        with TemporaryDirectory() as tmp:
            store = FormulaStore(Path(tmp) / "formula_candidates.jsonl")
            first = {"id": "FORM-MOIST-001", "request_id": "REQ-001", "score": {"overall": 0.8}}
            second = {"id": "FORM-MOIST-001", "request_id": "REQ-002", "score": {"overall": 0.9}}

            self.assertEqual(1, store.append_many("REQ-001", "保湿", [first]))
            self.assertEqual(2, store.append_many("REQ-002", "保湿", [second]))

            latest = store.read_latest_by_formula("FORM-MOIST-001")

            self.assertEqual("REQ-002", latest["request_id"])
            self.assertEqual(0.9, latest["formula"]["score"]["overall"])
            self.assertIn("stored_at", latest)

    def test_reads_formulas_by_request(self):
        with TemporaryDirectory() as tmp:
            store = FormulaStore(Path(tmp) / "formula_candidates.jsonl")
            store.append_many(
                "REQ-001",
                "保湿",
                [
                    {"id": "FORM-MOIST-001", "score": {"overall": 0.8}},
                    {"id": "FORM-MOIST-002", "score": {"overall": 0.7}},
                ],
            )
            store.append_many("REQ-002", "修护", [{"id": "FORM-BARRIER-001", "score": {"overall": 0.6}}])

            rows = store.read_by_request("REQ-001")

            self.assertEqual(["FORM-MOIST-001", "FORM-MOIST-002"], [row["formula"]["id"] for row in rows])


if __name__ == "__main__":
    unittest.main()
