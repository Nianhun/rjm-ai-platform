import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.http_server import FormulaAIHandler, run_server
from rjm_formula_ai.screening_store import ScreeningStore
from rjm_formula_ai.service import FormulaAIService


ROOT = Path(__file__).resolve().parents[3]


class ScreeningStoreTest(unittest.TestCase):
    def test_append_and_filter_screening_records(self):
        with TemporaryDirectory() as tmp:
            store = ScreeningStore(Path(tmp) / "screening_events.jsonl")
            store.append({"formula_id": "FORM-MOIST-001", "decision": "keep", "reason": "suitable for pilot"})
            store.append({"formula_id": "FORM-MOIST-002", "decision": "reject", "reason": "skin feel risk"})

            records = store.read_by_formula("FORM-MOIST-001")

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["decision"], "keep")


class ScreeningServiceTest(unittest.TestCase):
    def test_record_and_list_screening(self):
        with TemporaryDirectory() as tmp:
            service = FormulaAIService.from_project_root(
                ROOT,
                feedback_path=Path(tmp) / "feedback_events.jsonl",
                screening_path=Path(tmp) / "screening_events.jsonl",
            )

            reason = "moisturizing logic is clear; move to pilot test"
            stored = service.record_screening(
                {
                    "formula_id": "FORM-MOIST-001",
                    "engineer": "formula_engineer",
                    "decision": "keep",
                    "reason": reason,
                    "modified_ingredients": [],
                }
            )
            records = service.list_screening("FORM-MOIST-001")

            self.assertEqual(stored["stored"], True)
            self.assertEqual(stored["screening_count"], 1)
            self.assertEqual(records["formula_id"], "FORM-MOIST-001")
            self.assertEqual(records["records"][0]["reason"], reason)


class ScreeningHttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        FormulaAIHandler.service = FormulaAIService.from_project_root(
            ROOT,
            feedback_path=Path(cls.tmp.name) / "feedback_events.jsonl",
            screening_path=Path(cls.tmp.name) / "screening_events.jsonl",
        )
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

    def test_http_screening_record_and_query(self):
        conn = HTTPConnection("127.0.0.1", self.port, timeout=5)
        body = json.dumps(
            {
                "formula_id": "FORM-MOIST-HTTP-001",
                "engineer": "formula_engineer",
                "decision": "reject",
                "reason": "supply chain risk is high",
                "modified_ingredients": [],
            }
        )
        conn.request("POST", "/screening", body=body.encode("utf-8"), headers={"Content-Type": "application/json"})
        post_response = conn.getresponse()
        post_payload = json.loads(post_response.read().decode("utf-8"))
        conn.close()

        query = HTTPConnection("127.0.0.1", self.port, timeout=5)
        query.request("GET", "/screening?formula_id=FORM-MOIST-HTTP-001")
        get_response = query.getresponse()
        get_payload = json.loads(get_response.read().decode("utf-8"))
        query.close()

        self.assertEqual(post_response.status, 200)
        self.assertEqual(post_payload["stored"], True)
        self.assertEqual(get_response.status, 200)
        self.assertEqual(get_payload["records"][0]["decision"], "reject")


if __name__ == "__main__":
    unittest.main()
