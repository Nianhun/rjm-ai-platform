import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.feedback_store import FeedbackStore
from rjm_formula_ai.http_server import FormulaAIHandler, run_server
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class FeedbackStoreTest(unittest.TestCase):
    def test_append_and_read_feedback_events(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "feedback_events.jsonl"
            store = FeedbackStore(path)

            store.append({"result": "pass", "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"]})
            store.append({"result": "fail", "ingredient_ids": ["ING-PANTHENOL", "ING-BETAINE"]})

            events = store.read_all()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["result"], "pass")
            self.assertEqual(events[1]["result"], "fail")


class PersistentFeedbackServiceTest(unittest.TestCase):
    def test_recorded_feedback_affects_new_service_instance(self):
        with TemporaryDirectory() as tmp:
            feedback_path = Path(tmp) / "feedback_events.jsonl"
            service = FormulaAIService.from_project_root(ROOT, feedback_path=feedback_path)
            before = service.recommend({"id": "REQ-PERSIST-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})
            service.record_feedback(
                {
                    "result": "pass",
                    "ingredient_ids": [
                        item["ingredient_id"]
                        for item in before["formulas"][0]["ingredients"]
                    ],
                    "formula_id": before["formulas"][0]["id"]
                }
            )

            reloaded = FormulaAIService.from_project_root(ROOT, feedback_path=feedback_path)
            after = reloaded.recommend({"id": "REQ-PERSIST-001", "goal": "保湿", "dosage_form": "乳液", "constraints": {}})

            before_scores = [item["score"]["overall"] for item in before["formulas"]]
            after_scores = [item["score"]["overall"] for item in after["formulas"]]
            self.assertNotEqual(before_scores, after_scores)


class FeedbackHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        cls.feedback_path = Path(cls.tmp.name) / "feedback_events.jsonl"
        FormulaAIHandler.service = FormulaAIService.from_project_root(ROOT, feedback_path=cls.feedback_path)
        cls.server = run_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.tmp.cleanup()

    def test_http_feedback_records_event(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps(
            {
                "result": "pass",
                "ingredient_ids": ["ING-GLYCERIN", "ING-SODIUM-HYALURONATE"],
                "formula_id": "FORM-MOIST-TEST"
            }
        )
        conn.request("POST", "/feedback", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        conn.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["stored"], True)
        self.assertEqual(payload["feedback_count"], 1)


if __name__ == "__main__":
    unittest.main()

