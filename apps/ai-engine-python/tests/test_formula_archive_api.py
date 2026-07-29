import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.http_server import FormulaAIHandler, run_server
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class FormulaArchiveApiTest(unittest.TestCase):
    def test_service_archives_recommendation_candidates(self):
        with TemporaryDirectory() as tmp:
            formula_path = Path(tmp) / "formula_candidates.jsonl"
            service = FormulaAIService.from_project_root(ROOT, formula_path=formula_path)

            recommendation = service.recommend({"id": "REQ-ARCHIVE-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
            formula_id = recommendation["formulas"][0]["id"]
            archived = service.get_archived_formula(formula_id)

            self.assertEqual(formula_id, archived["formula_id"])
            self.assertEqual("REQ-ARCHIVE-001", archived["request_id"])
            self.assertEqual(formula_id, archived["formula"]["id"])

    def test_http_returns_archived_formula_after_recommendation(self):
        with TemporaryDirectory() as tmp:
            formula_path = Path(tmp) / "formula_candidates.jsonl"
            FormulaAIHandler.service = FormulaAIService.from_project_root(ROOT, formula_path=formula_path)
            server = run_server("127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                body = json.dumps({"id": "REQ-ARCHIVE-HTTP", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
                conn.request("POST", "/recommend", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
                recommend_response = conn.getresponse()
                recommendation = json.loads(recommend_response.read().decode("utf-8"))
                formula_id = recommendation["formulas"][0]["id"]
                conn.close()

                conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                conn.request("GET", f"/formulas/{formula_id}")
                response = conn.getresponse()
                archived = json.loads(response.read().decode("utf-8"))
                conn.close()

                self.assertEqual(200, response.status)
                self.assertEqual(formula_id, archived["formula_id"])
                self.assertEqual("REQ-ARCHIVE-HTTP", archived["request_id"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()

