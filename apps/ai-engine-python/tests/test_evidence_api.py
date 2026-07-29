import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.http_server import FormulaAIHandler, run_server
from rjm_formula_ai.service import FormulaAIService


def write_minimal_knowledge(root: Path) -> tuple[Path, Path, Path, Path]:
    ingredients_path = root / "ingredients.json"
    relations_path = root / "relations.json"
    evidence_path = root / "evidence.json"
    skus_path = root / "raw_material_skus.json"

    ingredients_path.write_text(
        json.dumps(
            [
                {
                    "id": "ING-GLYCERIN",
                    "name_cn": "Glycerin",
                    "name_en": "Glycerin",
                    "inci_name": "GLYCERIN",
                    "category": "humectant",
                    "functions": ["保湿"],
                    "properties": {},
                    "usage_range": {"min_percent": 1.0, "max_percent": 5.0, "typical_percent": 3.0},
                    "regulatory_limits": [],
                    "risk_tags": [],
                    "evidence_ids": ["YUXI-ING-GLYCERIN"],
                }
            ]
        ),
        encoding="utf-8",
    )
    relations_path.write_text("[]\n", encoding="utf-8")
    evidence_path.write_text(
        json.dumps(
            [
                {
                    "id": "YUXI-ING-GLYCERIN",
                    "source_type": "ingredient_profile",
                    "title": "Glycerin",
                    "summary": "Classic moisturizing ingredient.",
                    "source_url": "https://incidecoder.com/ingredients/glycerin",
                    "metadata": {"ingredient_id": "ING-GLYCERIN"},
                }
            ]
        ),
        encoding="utf-8",
    )
    skus_path.write_text("[]\n", encoding="utf-8")
    return ingredients_path, relations_path, skus_path, evidence_path


class EvidenceApiTest(unittest.TestCase):
    def test_service_returns_evidence_by_id(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ingredients_path, relations_path, skus_path, evidence_path = write_minimal_knowledge(root)
            service = FormulaAIService.from_project_root(
                root,
                ingredients_path=ingredients_path,
                relations_path=relations_path,
                raw_material_skus_path=skus_path,
                evidence_path=evidence_path,
            )

            evidence = service.get_evidence("YUXI-ING-GLYCERIN")

            self.assertEqual(evidence["id"], "YUXI-ING-GLYCERIN")
            self.assertEqual(evidence["source_type"], "ingredient_profile")
            self.assertEqual(evidence["source_url"], "https://incidecoder.com/ingredients/glycerin")

    def test_http_returns_404_for_unknown_evidence(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ingredients_path, relations_path, skus_path, evidence_path = write_minimal_knowledge(root)
            FormulaAIHandler.service = FormulaAIService.from_project_root(
                root,
                ingredients_path=ingredients_path,
                relations_path=relations_path,
                raw_material_skus_path=skus_path,
                evidence_path=evidence_path,
            )
            server = run_server("127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                conn.request("GET", "/evidence/UNKNOWN")
                response = conn.getresponse()
                payload = json.loads(response.read().decode("utf-8"))
                conn.close()

                self.assertEqual(response.status, 404)
                self.assertEqual(payload["error"], "evidence_not_found")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_http_returns_known_evidence(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ingredients_path, relations_path, skus_path, evidence_path = write_minimal_knowledge(root)
            FormulaAIHandler.service = FormulaAIService.from_project_root(
                root,
                ingredients_path=ingredients_path,
                relations_path=relations_path,
                raw_material_skus_path=skus_path,
                evidence_path=evidence_path,
            )
            server = run_server("127.0.0.1", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                conn.request("GET", "/evidence/YUXI-ING-GLYCERIN")
                response = conn.getresponse()
                payload = json.loads(response.read().decode("utf-8"))
                conn.close()

                self.assertEqual(response.status, 200)
                self.assertEqual(payload["id"], "YUXI-ING-GLYCERIN")
                self.assertEqual(payload["title"], "Glycerin")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
