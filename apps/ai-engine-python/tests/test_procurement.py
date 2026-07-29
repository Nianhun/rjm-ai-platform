import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path

from rjm_formula_ai.http_server import FormulaAIHandler, run_server
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class ProcurementServiceTest(unittest.TestCase):
    def test_recommend_procurement_returns_skus_for_formula_ingredients(self):
        service = FormulaAIService.from_project_root(ROOT)
        formula = service.recommend({"id": "REQ-PROC-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})["formulas"][0]

        response = service.recommend_procurement({"formula": formula})

        self.assertEqual(response["formula_id"], formula["id"])
        self.assertGreaterEqual(len(response["items"]), 1)
        first_item = response["items"][0]
        self.assertIn("ingredient_id", first_item)
        self.assertIn("recommended_skus", first_item)
        self.assertGreaterEqual(len(first_item["recommended_skus"]), 1)
        self.assertGreater(first_item["recommended_skus"][0]["procurement_score"], 0)

    def test_procurement_marks_missing_supplier_for_unsourced_ingredient(self):
        service = FormulaAIService.from_project_root(ROOT)

        response = service.recommend_procurement(
            {
                "formula": {
                    "id": "FORM-PROC-MISSING",
                    "ingredients": [
                        {
                            "ingredient_id": "ING-CERAMIDE-NP",
                            "role": "屏障修护",
                            "suggested_percent_min": 0.01,
                            "suggested_percent_max": 0.05
                        }
                    ]
                }
            }
        )

        self.assertEqual(response["items"][0]["status"], "missing_supplier")
        self.assertEqual(response["items"][0]["recommended_skus"], [])


class ProcurementHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FormulaAIHandler.service = FormulaAIService.from_project_root(ROOT)
        cls.server = run_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_http_procurement_endpoint(self):
        service = FormulaAIService.from_project_root(ROOT)
        formula = service.recommend({"id": "REQ-PROC-HTTP-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})["formulas"][0]
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps({"formula": formula})
        conn.request("POST", "/procurement/recommend", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["formula_id"], formula["id"])
        self.assertGreaterEqual(len(payload["items"]), 1)


if __name__ == "__main__":
    unittest.main()

