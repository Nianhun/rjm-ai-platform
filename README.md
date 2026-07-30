# RJM Formula AI

RJM Formula AI is a local biomedical formula recommendation prototype. It combines a Python AI engine, a Spring Boot management API, a static engineer console, shared API/schema contracts, local sample data, and operational scripts.

## Architecture

```text
apps/ai-engine-python        Python AI engine and tests
apps/java-admin-service      Spring Boot management API
apps/engineer-console        Static engineer workbench UI
shared/api-contracts         OpenAPI contracts
shared/schemas               JSON Schemas
infrastructure/database      SQL schema drafts
scripts                      Demo, development, integration, and DB runners
data                         Samples, Yuxi imports, runtime state, outputs
docs                         Architecture, API, deployment, development, business docs
```

Key business acceptance doc: `docs/business/release_acceptance.md`.

Legacy paths are kept through compatibility directory links or wrapper scripts:

- `prototype/`
- `java-management/management-service/`
- `java-management/api-contract/`
- `java-management/database/`
- `ui/engineer-console/`
- `schemas/`
- `scripts/run_*.ps1`

## Environment

Copy `.env.example` when you need local overrides. Do not put real API keys, database passwords, or private tokens into committed files.

Important variables:

- `RJM_HTTP_HOST`, `RJM_HTTP_PORT`
- `RJM_FORMULA_PATH`, `RJM_FEEDBACK_PATH`, `RJM_SCREENING_PATH`
- `RJM_INGREDIENTS_PATH`, `RJM_RELATIONS_PATH`, `RJM_EVIDENCE_PATH`
- `RJM_YUXI_GRAPH_ENABLED`, `RJM_YUXI_API_BASE`, `RJM_YUXI_KB_ID`, `RJM_YUXI_API_TOKEN`
- `RJM_API_TOKEN_ENABLED`, `RJM_API_TOKEN`

## Local Start

Run the release demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_release_demo.ps1
```

Start the local Python AI + Java management + engineer console stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_prototype_stack.ps1 -UseYuxiKnowledge
```

Start the local stack with the online Yuxi graph settings loaded from `.env.local`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_online_stack.ps1
```

On first run, copy `.env.local.example` to `.env.local` and set `RJM_YUXI_API_TOKEN` if the Yuxi API requires authentication. `.env.local` is ignored by git.

Open:

```text
http://127.0.0.1:8080/console/index.html
```

Direct Python AI service:

```powershell
$env:PYTHONPATH="$PWD\apps\ai-engine-python\src"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m rjm_formula_ai.http_server
```

Direct Java service:

```powershell
cd F:\zky\RJM\apps\java-admin-service
mvn spring-boot:run
```

## Docker

No Dockerfile or Compose file is present in this repository yet. Docker validation is therefore not available until deployment artifacts are added.

## Tests

Python:

```powershell
$env:PYTHONPATH="$PWD\apps\ai-engine-python\src"
C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe apps\ai-engine-python\tests\test_release_acceptance.py
```

Java:

```powershell
cd F:\zky\RJM\apps\java-admin-service
mvn test
```

UI syntax:

```powershell
node --check apps\engineer-console\app.js
```

Integration smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_java_python_integration_smoke.ps1
```

## Common Issues

- If `pytest` is unavailable, run the Python test files directly with the bundled Python runtime.
- If Yuxi is not available, leave `RJM_YUXI_GRAPH_ENABLED=false`; the AI service falls back to local snapshot JSON.
- If old commands reference `prototype`, `java-management`, `ui`, or `schemas`, they should continue working through compatibility paths.
