# AI Engine Python

## Responsibility

Python AI engine for local formula recommendation, feedback learning, procurement matching, Yuxi import, Yuxi graph recall, and smoke/release demos.

## Tech Stack

- Python standard library
- JSON/JSONL file storage
- `http.server` based local HTTP adapter
- `unittest`/pytest-compatible tests

## Structure

```text
src/rjm_formula_ai/   Python package
tests/                Python behavior and smoke tests
README.md             This guide
```

## Environment

Set:

```powershell
$env:PYTHONPATH="$PWD\apps\ai-engine-python\src"
```

Important variables:

- `RJM_HTTP_HOST`, `RJM_HTTP_PORT`
- `RJM_INGREDIENTS_PATH`, `RJM_RELATIONS_PATH`, `RJM_RAW_MATERIAL_SKUS_PATH`, `RJM_EVIDENCE_PATH`
- `RJM_FORMULA_PATH`, `RJM_FEEDBACK_PATH`, `RJM_SCREENING_PATH`
- `RJM_YUXI_GRAPH_ENABLED`, `RJM_YUXI_API_BASE`, `RJM_YUXI_KB_ID`, `RJM_YUXI_API_TOKEN`

## Start

```powershell
$env:PYTHONPATH="$PWD\apps\ai-engine-python\src"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m rjm_formula_ai.http_server
```

Legacy mode remains available:

```powershell
$env:PYTHONPATH="$PWD\prototype"
python -m rjm_formula_ai.http_server
```

## Tests

```powershell
$env:PYTHONPATH="$PWD\apps\ai-engine-python\src"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe apps\ai-engine-python\tests\test_release_acceptance.py
```

## External Interfaces

The Python service exposes:

- `GET /health`
- `GET /knowledge/status`
- `GET /knowledge/governance`
- `GET /evidence/{evidence_id}`
- `GET /formulas/{formula_id}`
- `POST /recommend`
- `POST /feedback`
- `POST /feedback/recommend`
- `POST /procurement/recommend`
- `POST /reports/feedback-impact`
- `POST /screening`
- `GET /screening?formula_id=...`

## Dependencies

- Local data under `data/`
- Shared schemas under `shared/schemas/`
- Optional Yuxi graph HTTP API
- Java management service calls this service in `python` mode
