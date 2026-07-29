import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .feedback_report import build_feedback_impact_report
from .service import FormulaAIService
from .yuxi_graph_client import HttpYuxiGateway, YuxiGraphClient


class FormulaAIHandler(BaseHTTPRequestHandler):
    service: FormulaAIService | None = None

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path == "/knowledge/status":
            self._send_json(200, self._service().knowledge_status())
            return
        if self.path == "/knowledge/governance":
            self._send_json(200, self._service().knowledge_governance())
            return
        parsed = urlparse(self.path)
        if parsed.path.startswith("/evidence/"):
            evidence_id = unquote(parsed.path[len("/evidence/") :])
            evidence = self._service().get_evidence(evidence_id)
            if evidence is None:
                self._send_json(404, {"error": "evidence_not_found", "evidence_id": evidence_id})
            else:
                self._send_json(200, evidence)
            return
        if parsed.path.startswith("/formulas/"):
            formula_id = unquote(parsed.path[len("/formulas/") :])
            archived = self._service().get_archived_formula(formula_id)
            if archived is None:
                self._send_json(404, {"error": "formula_not_found", "formula_id": formula_id})
            else:
                self._send_json(200, archived)
            return
        if parsed.path == "/screening":
            query = parse_qs(parsed.query)
            formula_id = query.get("formula_id", [""])[0]
            self._send_json(200, self._service().list_screening(formula_id))
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        try:
            payload = self._read_json()
            if self.path == "/recommend":
                self._send_json(200, self._service().recommend(payload))
                return
            if self.path == "/feedback/recommend":
                self._send_json(200, self._service().feedback_recommend(payload))
                return
            if self.path == "/feedback":
                self._send_json(200, self._service().record_feedback(payload))
                return
            if self.path == "/procurement/recommend":
                self._send_json(200, self._service().recommend_procurement(payload))
                return
            if self.path == "/reports/feedback-impact":
                self._send_json(200, build_feedback_impact_report(self._service(), payload))
                return
            if self.path == "/screening":
                self._send_json(200, self._service().record_screening(payload))
                return
            self._send_json(404, {"error": "not_found"})
        except KeyError as exc:
            self._send_json(400, {"error": "missing_field", "field": str(exc).strip("'")})
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _service(self) -> FormulaAIService:
        if self.service is None:
            project_root = Path(__file__).resolve().parents[3]
            self.__class__.service = build_service_from_environment(project_root)
        return self.service

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def build_service_from_environment(project_root: Path) -> FormulaAIService:
    ingredients_path = _optional_path(os.environ.get("RJM_INGREDIENTS_PATH"))
    relations_path = _optional_path(os.environ.get("RJM_RELATIONS_PATH"))
    raw_material_skus_path = _optional_path(os.environ.get("RJM_RAW_MATERIAL_SKUS_PATH"))
    evidence_path = _optional_path(os.environ.get("RJM_EVIDENCE_PATH"))
    formula_path = _optional_path(os.environ.get("RJM_FORMULA_PATH"))
    feedback_path = _optional_path(os.environ.get("RJM_FEEDBACK_PATH"))
    screening_path = _optional_path(os.environ.get("RJM_SCREENING_PATH"))
    yuxi_graph_client = _yuxi_graph_client_from_environment()
    return FormulaAIService.from_project_root(
        project_root,
        ingredients_path=ingredients_path,
        relations_path=relations_path,
        raw_material_skus_path=raw_material_skus_path,
        evidence_path=evidence_path,
        formula_path=formula_path,
        feedback_path=feedback_path,
        screening_path=screening_path,
        yuxi_graph_client=yuxi_graph_client,
    )


def _optional_path(value: str | None) -> Path | None:
    return Path(value) if value else None


def _yuxi_graph_client_from_environment() -> YuxiGraphClient | None:
    enabled = os.environ.get("RJM_YUXI_GRAPH_ENABLED", "").lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return None
    base_url = os.environ.get("RJM_YUXI_API_BASE", "http://127.0.0.1:5050")
    token = os.environ.get("RJM_YUXI_API_TOKEN") or None
    kb_id = os.environ.get("RJM_YUXI_KB_ID") or None
    return YuxiGraphClient(HttpYuxiGateway(base_url, token=token), kb_id=kb_id)


def server_config_from_environment() -> tuple[str, int]:
    host = os.environ.get("RJM_HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("RJM_HTTP_PORT", "8787"))
    return host, port


def run_server(host: str = "127.0.0.1", port: int = 8787) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), FormulaAIHandler)


def main() -> None:
    host, port = server_config_from_environment()
    server = run_server(host, port)
    print(f"RJM Formula AI HTTP service listening on http://{host}:{port}")
    print("GET /knowledge/status")
    print("GET /knowledge/governance")
    print("GET /evidence/{evidence_id}")
    print("GET /formulas/{formula_id}")
    print("POST /recommend")
    print("POST /feedback/recommend")
    print("POST /reports/feedback-impact")
    print("POST /screening")
    print("GET /screening?formula_id=FORM-MOIST-001")
    server.serve_forever()


if __name__ == "__main__":
    main()

