# Migration Report

## Before

The repository mixed runnable projects, contracts, schema files, scripts, runtime outputs, and source documents at the root. `prototype`, `java-management`, `ui`, and `schemas` were stable paths used by scripts and tests, so moving them required compatibility handling.

## After

```text
apps/
  ai-engine-python/
  java-admin-service/
  engineer-console/
shared/
  api-contracts/java-management/
  schemas/
infrastructure/
  database/java-management/
scripts/
  demo/
  development/
  integration/
  database/
docs/
  architecture/
  api/
  deployment/
  development/
  business/
```

## File Migration List

| Old Path | New Path | Notes |
| --- | --- | --- |
| `prototype/rjm_formula_ai` | `apps/ai-engine-python/src/rjm_formula_ai` | Python package moved under AI app. |
| `prototype/tests` | `apps/ai-engine-python/tests` | Python tests moved with AI app. |
| `prototype/README.md` | `apps/ai-engine-python/README.md` | AI app README moved; old README is a compatibility note. |
| `java-management/management-service` | `apps/java-admin-service` | Spring Boot service moved under apps. |
| `ui/engineer-console` | `apps/engineer-console` | Static console moved under apps. |
| `java-management/api-contract` | `shared/api-contracts/java-management` | OpenAPI contract moved to shared. |
| `schemas` | `shared/schemas` | JSON Schemas moved to shared. |
| `java-management/database` | `infrastructure/database/java-management` | SQL schema drafts moved to infrastructure. |
| `scripts/run_*.ps1` | `scripts/{demo,development,integration,database}/` | Implementations grouped by purpose; root wrappers remain. |
| `docs/api_service.md` | `docs/api/api_service.md` | API docs grouped. |
| `docs/deployment_runbook.md` | `docs/deployment/deployment_runbook.md` | Deployment docs grouped. |
| `docs/product_brief.md` | `docs/business/product_brief.md` | Business docs grouped. |
| `docs/release_acceptance.md` | `docs/business/release_acceptance.md` | Release acceptance docs grouped. |

## Renames

No Python package, Java package, API path, JSON field, database table, or business method was renamed. Project folders were reorganized only.

## Configuration Changes

- Python `PYTHONPATH` now points to `apps/ai-engine-python/src`.
- Java local DB schema path now points to `../../infrastructure/database/java-management/schema.h2.sql`.
- Java console static resource default now points to `apps/engineer-console`.
- `application-db-local.yml` no longer hardcodes `F:/zky/RJM` for the local H2 file path.

## Compatibility

The following legacy paths remain available:

- `prototype/rjm_formula_ai`
- `prototype/tests`
- `java-management/management-service`
- `java-management/api-contract`
- `java-management/database`
- `ui/engineer-console`
- `schemas`
- root `scripts/run_*.ps1`

## Test Results

| Check | Result | Notes |
| --- | --- | --- |
| `F:\zky\SWE-bench\SWE-bench-main\python310\python.exe -m compileall apps\ai-engine-python\src apps\ai-engine-python\tests` | Passed | Python 3.10 is required for the existing `list[str]` type annotations. |
| Python test runner over `apps\ai-engine-python\tests\test_*.py` | Passed | 73 Python tests/checks passed. `pytest` is not installed in the active `python` environment, so no dependency was added. |
| `mvn test` in `apps\java-admin-service` | Passed | 61 tests, 0 failures, 0 errors, 1 skipped. |
| `node --check apps\engineer-console\app.js` | Passed | Static console JavaScript syntax is valid. |
| `powershell -ExecutionPolicy Bypass -File .\scripts\run_prototype_stack.ps1 -SmokeOnly` | Passed | Start URLs and runtime log paths are parseable after restructuring. |
| `git status --short` | Not applicable | The working directory is not a Git repository. |
| `git diff --stat` | Not applicable | The working directory is not a Git repository. |
| `ruff check .` | Not executed | Ruff is not installed and was not added as a new dependency. |
| `docker compose config` / `docker compose build` | Not applicable | No Dockerfile or Compose file exists in this repository snapshot. |
| External Yuxi, PostgreSQL, Redis, MinIO, Milvus, Neo4j connectivity | Not verified | Required external services/credentials are not present locally. |

## Risks And Follow-Up

- This directory is not a Git repository, so `git status`, `git diff`, `git mv`, and commit-based rollback are unavailable.
- Directory links are used for compatibility on Windows. If the project is later copied to an environment that does not preserve junctions, recreate the links or update old commands.
- Historical docs under `docs/agent_handoff.md` and `docs/implementation_10_phase/` intentionally retain old command records as history.
