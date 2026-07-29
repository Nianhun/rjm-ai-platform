# Agent Handoff

## Current Status

- Project stage: Python prototype plus Java management service initial release 10/10 complete.
- Main goal: build moisturizing formula recommendation loop.
- Latest completed task: Phase 10 initial release acceptance demo.
- Git status: `F:\zky\RJM` is not a git repository, so commit steps are recorded but not executed.

## How To Resume

1. Read `docs/superpowers/plans/2026-07-27-rjm-formula-ai-development-plan.md`.
2. Read this file.
3. Read `docs/implementation_10_phase_plan.md`.
4. Run the latest verification command listed below.
5. Continue with the first incomplete phase under `docs/implementation_10_phase/`.

## Verification Log

| Date | Task | Command | Expected | Result |
| --- | --- | --- | --- | --- |
| 2026-07-27 | Task 1 | `Get-ChildItem docs,schemas,data,prototype` | directories exist | pass |
| 2026-07-27 | Task 2 | `Get-ChildItem schemas -Filter '*.json' | ForEach-Object { python -m json.tool $_.FullName }` | all schemas parse | pass |
| 2026-07-27 | Task 3 | `Get-ChildItem data\samples -Filter '*.json' | ForEach-Object { python -m json.tool $_.FullName }` | all samples parse | pass |
| 2026-07-27 | Task 4 | bundled Python loader assertion command | loader returns 5 ingredients and 4 relations | pass |
| 2026-07-27 | Task 5 | bundled Python recommendation assertion command | 3 formulas generated with positive scores | pass |
| 2026-07-27 | Task 6 | bundled Python feedback assertion command | relation feedback weight increases from 0.0 to 0.05 | pass |
| 2026-07-27 | Task 7 | `$env:PYTHONPATH = "$PWD\prototype"; python -m rjm_formula_ai.cli` | before/after recommendation JSON files created | pass |
| 2026-07-27 | Task 8 | `Get-Content docs\yuxi_integration.md` | Yuxi integration notes exist | pass |
| 2026-07-27 | HTTP API | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_service_api.py` | service and HTTP endpoint tests pass | pass |
| 2026-07-27 | Procurement API | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_procurement.py` | procurement service and HTTP endpoint tests pass | pass |
| 2026-07-27 | Persistent Feedback | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_feedback_store.py` | feedback store and HTTP feedback tests pass | pass |
| 2026-07-27 | Engineer Screening | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_screening.py` | screening store and HTTP endpoint tests pass | pass |
| 2026-07-28 | Engineer Review Client | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_engineer_client.py` | review rows and screening submission tests pass | pass |
| 2026-07-28 | Experiment Feedback Client | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_experiment_client.py` | feedback event builder, parser, and persistence tests pass | pass |
| 2026-07-28 | Feedback Impact Report | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_feedback_report.py` | baseline vs learned score comparison tests pass | pass |
| 2026-07-28 | Closed-Loop Workflow Smoke | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_workflow_smoke.py` | screening, feedback, impact report, and procurement flow passes | pass |
| 2026-07-28 | Java API Contract | `$env:PYTHONPATH = "$PWD\prototype"; python prototype\tests\test_java_contract_docs.py` | OpenAPI and Java contract README checks pass | pass |
| 2026-07-28 | Spring Boot Skeleton | `cd java-management\management-service; mvn test` | Java sources compile and Spring context loads | pass |
| 2026-07-28 | Spring Boot MockMvc Tests | `cd java-management\management-service; mvn test` | 6 endpoint tests plus context test pass | pass |
| 2026-07-28 | Java Python AI Client | `cd java-management\management-service; mvn test` | Python client unit test, MockMvc tests, and context test pass | pass |
| 2026-07-28 | Expanded Java Python AI Client | `cd java-management\management-service; mvn test` | Python client tests cover recommend, feedback, procurement, and report calls | pass |
| 2026-07-28 | Switchable Java AI Service Mode | `cd java-management\management-service; mvn test` | mock mode, Python client, and delegating service tests pass | pass |
| 2026-07-28 | Java Python Screening Delegation | `cd java-management\management-service; mvn test` | Python client and delegating service tests include screening write/read | pass |
| 2026-07-28 | Java Python Integration Smoke | `.\scripts\run_java_python_integration_smoke.ps1` | Java controllers in Python mode call the real Python HTTP service for recommendation, screening, feedback, and report flow | pass |
| 2026-07-28 | Yuxi Export Import Adapter | `.\scripts\run_yuxi_import.ps1` | Yuxi output imports into RJM ingredient and relation JSON files | pass |
| 2026-07-28 | Yuxi Knowledge Source Override | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_service_api.py; python prototype\tests\test_yuxi_import.py` | service can load imported knowledge through environment variables | pass |
| 2026-07-28 | Java Python Yuxi Integration Smoke | `.\scripts\run_java_python_integration_smoke.ps1 -UseYuxiKnowledge` | Java controllers call Python service backed by Yuxi-imported knowledge and receive `YUXI-` evidence IDs | pass |
| 2026-07-28 | Knowledge Status API | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_service_api.py; cd java-management\management-service; mvn test` | Python and Java expose loaded knowledge source status | pass |
| 2026-07-28 | Formula Engineer Static Console | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_engineer_console_ui.py; node --check ui\engineer-console\app.js` | static console files exist and target Java management workflow endpoints | pass |
| 2026-07-28 | Local Demo Launcher and UI Encoding Guard | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_http_server_config.py; python prototype\tests\test_engineer_console_ui.py; python prototype\tests\test_local_demo_script.py; node --check ui\engineer-console\app.js; PowerShell parser on scripts\run_local_demo.ps1` | Python HTTP port config, static UI copy, demo script, JS syntax, and PowerShell syntax pass | pass |
| 2026-07-28 | Java-hosted Engineer Console and CORS | `cd java-management\management-service; mvn -Dtest=ManagementConsoleWebTests test` | Java root redirects to console, `/console/index.html` serves the static UI, and API CORS preflight passes | pass |
| 2026-07-28 | Yuxi Evidence Catalog and Traceability API | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_yuxi_import.py; python prototype\tests\test_evidence_api.py; cd java-management\management-service; mvn test; .\scripts\run_java_python_integration_smoke.ps1 -UseYuxiKnowledge` | Yuxi import writes evidence catalog, Python and Java expose evidence lookup, and Yuxi integration can resolve `YUXI-ING-GLYCERIN` | pass |
| 2026-07-28 | Formula Candidate Archive and Lookup API | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_formula_store.py; python prototype\tests\test_formula_archive_api.py; python prototype\tests\test_java_contract_docs.py; cd java-management\management-service; mvn -Dtest=ManagementApiMockMvcTests,PythonFormulaAiClientTests,PythonDelegatingFormulaAiManagementServiceTests test` | Python archives recommendation candidates, Python and Java expose lookup by formula id, and OpenAPI documents the archive response | pass |
| 2026-07-28 | Java Management Database Schema Draft | `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_database_schema.py` | SQLite-compatible schema defines closed-loop persistence tables and README records one-person delivery path | pass |
| 2026-07-28 | Java Formula Archive JDBC Repository Boundary | `cd java-management\management-service; mvn test` | Repository can save recommendation snapshots to formula archive tables, load latest archived formula by ID, and all Java tests pass | pass |
| 2026-07-28 | Java DB Service Mode for Formula Archive | `cd java-management\management-service; mvn -Dtest=DbModeManagementApiTests,DbArchivingFormulaAiManagementServiceTests test` | `rjm.ai-service.mode=db` selects the DB archiving service, recommendations are archived through the repository, and archive lookup reads from the repository | pass |
| 2026-07-28 | Java DB Mode H2 Integration Smoke | `cd java-management\management-service; mvn -Dtest=DbModeH2IntegrationTests test` | `db` mode runs against a real H2 in-memory database, writes recommendation snapshots, and reads archived formula data through the HTTP API | pass |
| 2026-07-28 | Java DB Screening Persistence | `cd java-management\management-service; mvn -Dtest=FormulaScreeningRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeH2IntegrationTests test` | DB mode writes and reads engineer screening records through JDBC and verifies the path against H2 | pass |
| 2026-07-28 | Java DB Experiment Feedback Persistence | `cd java-management\management-service; mvn -Dtest=ExperimentFeedbackRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeManagementApiTests,DbModeH2IntegrationTests test` | DB mode writes experiment feedback through JDBC, exposes it through the API, and verifies the path against H2 | pass |
| 2026-07-28 | Java DB Feedback Impact Report Counts | `cd java-management\management-service; mvn -Dtest=DbArchivingFormulaAiManagementServiceTests,DbModeManagementApiTests,DbModeH2IntegrationTests test` | DB mode feedback impact reports count persisted feedback for returned formula rows | pass |
| 2026-07-28 | Java DB Recommendation Feedback Boost | `cd java-management\management-service; mvn -Dtest=ExperimentFeedbackRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeH2IntegrationTests test` | DB mode counts passing feedback, boosts matching formula scores, reranks candidates, and archives the learned order | pass |
| 2026-07-28 | Java DB Ingredient Feedback Boost | `cd java-management\management-service; mvn -Dtest=ExperimentFeedbackRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeH2IntegrationTests test` | DB mode counts passing feedback by ingredient, boosts formulas containing historically successful ingredients, and verifies reranking against H2 | pass |
| 2026-07-28 | Java DB Ingredient-Pair Feedback Boost | `cd java-management\management-service; mvn -Dtest=ExperimentFeedbackRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeH2IntegrationTests test` | DB mode counts passing feedback by ingredient pair, boosts formulas containing historically successful pairs, and verifies the path against H2 | pass |
| 2026-07-28 | Java DB Learned Weight Audit Table | `cd java-management\management-service; mvn -Dtest=LearnedWeightRepositoryTests,DbArchivingFormulaAiManagementServiceTests,DbModeH2IntegrationTests test` | DB mode persists formula, ingredient, and ingredient-pair feedback weights into `learned_weight`, including capped weights and evidence counts | pass |
| 2026-07-28 | 10 Phase Initial Release Plan | `Get-ChildItem docs\implementation_10_phase; Get-Content docs\implementation_10_phase_plan.md` | master plan and 10 phase documents exist for agent-driven initial release delivery | pass |
| 2026-07-28 | Phase 02 Java Local DB Runtime Config | `powershell -ExecutionPolicy Bypass -File .\scripts\run_java_db_local.ps1 -SmokeOnly` | `db-local` profile creates an H2 DataSource, initializes schema, and keeps H2 integration path green | pass |
| 2026-07-28 | Phase 03 Learned Weight API and Explanation | `cd java-management\management-service; mvn "-Dtest=LearningControllerTests,LearnedWeightRepositoryTests,DbModeH2IntegrationTests" test; cd F:\zky\RJM; python prototype\tests\test_engineer_console_ui.py; node --check ui\engineer-console\app.js; python prototype\tests\test_java_contract_docs.py` | Java exposes learned weight audit/explanation APIs, H2 verifies persisted influence rows, console targets the endpoints, and OpenAPI documents them | pass |
| 2026-07-28 | Phase 04 Engineer Console Workbench | `cd F:\zky\RJM; python prototype\tests\test_engineer_console_ui.py; node --check ui\engineer-console\app.js; cd java-management\management-service; mvn "-Dtest=ManagementConsoleWebTests,ManagementApiMockMvcTests" test` | static console exposes operation status, selected formula summary, action status wrapping, and Java-hosted console tests cover the new shell structure | pass |
| 2026-07-28 | Phase 05 Supplier Procurement Loop | `cd java-management\management-service; mvn "-Dtest=ProcurementRecommendationRepositoryTests,DbModeH2IntegrationTests,ManagementApiMockMvcTests" test; cd F:\zky\RJM; python prototype\tests\test_engineer_console_ui.py; node --check ui\engineer-console\app.js; python prototype\tests\test_java_contract_docs.py` | DB mode persists procurement recommendations, query/status APIs work through H2, console targets saved procurement and sample request actions, and OpenAPI documents the flow | pass |

## Completed Tasks

- Task 1: project skeleton and handoff docs.
- Task 2: JSON Schemas.
- Task 3: moisturizing sample data.
- Task 4: Python models and data loader.
- Task 5: formula recommendation prototype.
- Task 6: feedback learning.
- Task 7: end-to-end CLI demo.
- Task 8: Yuxi integration notes.

## Task 2 Notes

- JSON Schemas created under `schemas/`.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: create moisturizing sample data and validate against schemas.

## Task 3 Notes

- Moisturizing sample data created under `data/samples/`.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: implement Python prototype models and loader.

## Task 4 Notes

- Python dataclass models and JSON loaders created under `prototype/rjm_formula_ai/`.
- `pytest` is not installed in the available Python runtimes, so tests are verified with direct Python execution for now.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: implement formula recommendation prototype.

## Task 5 Notes

- Formula recommendation prototype created in `prototype/rjm_formula_ai/recommend.py`.
- Recommender returns 3 formula candidates with ingredients, evidence, risk notes, and scores.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: implement feedback learning.

## Task 6 Notes

- Feedback learning created in `prototype/rjm_formula_ai/feedback.py`.
- Passing experiment feedback increases matching ingredient relation `feedback_weight`; non-pass feedback decreases it.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: create end-to-end CLI demo.

## Task 7 Notes

- End-to-end CLI demo created in `prototype/rjm_formula_ai/cli.py`.
- PowerShell runner created at `scripts/run_formula_demo.ps1`.
- Demo writes before/after recommendation JSON files under `data/outputs/`.
- Commit step skipped because `F:\zky\RJM` is not a git repository.
- Next task: create Yuxi integration notes.

## Task 8 Notes

- Yuxi integration notes created in `docs/yuxi_integration.md`.
- Later Yuxi work must begin by reading `docs/yuxi_integration.md`.
- Commit step skipped because `F:\zky\RJM` is not a git repository.

## HTTP API Notes

- Service layer created in `prototype/rjm_formula_ai/service.py`.
- Zero-dependency HTTP adapter created in `prototype/rjm_formula_ai/http_server.py`.
- API contract documented in `docs/api_service.md`.
- FastAPI/uvicorn install was blocked by environment dependency issues, so the adapter is intentionally replaceable.

## Procurement API Notes

- Raw material SKU loading added via `load_raw_material_skus`.
- Procurement matching added in `prototype/rjm_formula_ai/procurement.py`.
- HTTP endpoint added: `POST /procurement/recommend`.
- Procurement results sort matched suppliers before missing supplier records.

## Persistent Feedback Notes

- Feedback event log added at `data/runtime/feedback_events.jsonl`.
- Store implementation added in `prototype/rjm_formula_ai/feedback_store.py`.
- HTTP endpoint added: `POST /feedback`.
- `FormulaAIService.recommend` now applies historical feedback from the event log before ranking formulas.

## Engineer Screening Notes

- Screening event log added at `data/runtime/screening_events.jsonl`.
- Store implementation added in `prototype/rjm_formula_ai/screening_store.py`.
- HTTP endpoints added: `POST /screening` and `GET /screening?formula_id=...`.
- Screening records do not mutate AI recommendations; they preserve engineer decisions and reasons for later experiment selection.

## Engineer Review Client Notes

- Command-line client added in `prototype/rjm_formula_ai/engineer_client.py`.
- PowerShell runner added at `scripts/run_engineer_review.ps1`.
- Client lists candidate summaries with formula id, score, ingredient ids, risk summary, and recommendation reason.
- Client can record keep/reject/modify decisions through `FormulaAIService.record_screening`.

## Experiment Feedback Client Notes

- Command-line client added in `prototype/rjm_formula_ai/experiment_client.py`.
- PowerShell runner added at `scripts/run_experiment_feedback.ps1`.
- Client records lab outcomes with formula id, batch number, result, ingredient ids, metrics, issues, engineer conclusion, engineer, and timestamp.
- Records are appended through `FormulaAIService.record_feedback`, so later recommendation calls apply them via the persistent feedback store.

## Feedback Impact Report Notes

- Report command added in `prototype/rjm_formula_ai/feedback_report.py`.
- PowerShell runner added at `scripts/run_feedback_report.ps1`.
- Report compares baseline recommendations from sample graph data against learned recommendations that include persisted feedback.
- Output rows include formula id, baseline rank, learned rank, baseline score, learned score, score delta, and ingredient ids.

## Closed-Loop Workflow Smoke Notes

- Smoke workflow added in `prototype/rjm_formula_ai/workflow_smoke.py`.
- PowerShell runner added at `scripts/run_workflow_smoke.ps1`.
- Default CLI mode uses temporary feedback and screening logs, so it does not mutate `data/runtime`.
- `--persist` intentionally writes smoke feedback and screening records to runtime logs.
- The workflow covers recommendation, engineer screening, experiment feedback, feedback impact reporting, and procurement matching.

## Java Management API Contract Notes

- Java management contract directory added at `java-management/api-contract/`.
- OpenAPI 3.1 contract added at `java-management/api-contract/openapi.json`.
- Contract README added at `java-management/api-contract/README.md`.
- The contract mirrors Python prototype endpoints for recommendation, screening, feedback, procurement, and feedback impact reporting.
- This is intentionally a contract stub, not a full Spring Boot implementation.

## Spring Boot Management Service Notes

- Minimal Spring Boot service added at `java-management/management-service/`.
- Uses Spring Boot 2.7.18 because the local Java runtime is Java 8.
- Includes Controller classes for health, formula recommendation/screening, experiment feedback, procurement, and feedback impact reports.
- Includes Java 8 compatible DTO POJOs and `FormulaAiManagementService` service boundary.
- `InMemoryFormulaAiManagementService` is a mock implementation for management-system development before Python AI integration.
- Verified with `mvn test`; one Spring context test passed.

## Spring Boot MockMvc Test Notes

- MockMvc endpoint tests added in `java-management/management-service/src/test/java/com/rjm/formulaai/management/ManagementApiMockMvcTests.java`.
- Tests cover health, recommendation, screening write/read, experiment feedback, procurement recommendation, and feedback impact report endpoints.
- Added `src/main/resources/application.yml` with Jackson `SNAKE_CASE` naming so JSON fields match OpenAPI and Python prototype payloads.
- Verified with `mvn test`; 7 Java tests passed.

## Java Python AI Client Notes

- Python AI client added at `java-management/management-service/src/main/java/com/rjm/formulaai/management/client/PythonFormulaAiClient.java`.
- Client config and properties added under the same `client` package.
- Default Python AI base URL is `rjm.python-ai.base-url: http://127.0.0.1:8000`.
- Client methods call Python `POST /recommend`, `POST /feedback`, `POST /procurement/recommend`, and `POST /reports/feedback-impact`.
- Unit test `PythonFormulaAiClientTests` verifies the client sends snake_case JSON to Python endpoints.
- `InMemoryFormulaAiManagementService` remains the active management service; switch to the Python client only after deployment/error handling is designed.
- Python HTTP endpoint `POST /reports/feedback-impact` was added in `prototype/rjm_formula_ai/http_server.py`.

## Switchable Java AI Service Mode Notes

- Default mode configured in `java-management/management-service/src/main/resources/application.yml` as `rjm.ai-service.mode: mock`.
- `InMemoryFormulaAiManagementService` is active when mode is `mock` or missing.
- `PythonDelegatingFormulaAiManagementService` is active when mode is `python`.
- Python mode delegates recommendation, engineer screening write/read, experiment feedback, procurement, and feedback impact reports to `PythonFormulaAiClient`.
- Verified with `PythonDelegatingFormulaAiManagementServiceTests` and full `mvn test`.

## Java Python Screening Delegation Notes

- `PythonFormulaAiClient.recordFormulaScreening` now calls Python `POST /screening`.
- `PythonFormulaAiClient.listFormulaScreenings` now calls Python `GET /screening?formula_id=...`.
- `PythonDelegatingFormulaAiManagementService` delegates screening write/read to Python instead of local memory.
- `PythonFormulaAiClientTests` covers screening request and response mapping.

## Java Python Integration Smoke Notes

- Integration smoke test added at `java-management/management-service/src/test/java/com/rjm/formulaai/management/JavaPythonIntegrationSmokeTests.java`.
- PowerShell runner added at `scripts/run_java_python_integration_smoke.ps1`.
- The runner starts the Python HTTP service on `http://127.0.0.1:8787`, waits for `/health`, then runs the Java smoke test with `rjm.ai-service.mode=python`.
- The smoke flow covers Java API calls for recommendation, engineer screening write/read, experiment feedback, and feedback impact report against the real Python prototype.
- Runtime feedback and screening paths are redirected to a temporary directory via `RJM_FEEDBACK_PATH` and `RJM_SCREENING_PATH`, so this smoke test does not mutate `data/runtime`.
- `PythonFormulaAiClientConfig` uses Spring Boot's configured `ObjectMapper` in its RestTemplate so Python snake_case responses map correctly to Java camelCase DTOs.
- Default `mvn test` compiles the integration smoke test but skips it unless `rjm.integration.enabled=true` is set.

## Yuxi Export Import Adapter Notes

- Yuxi import adapter added at `prototype/rjm_formula_ai/yuxi_import.py`.
- PowerShell runner added at `scripts/run_yuxi_import.ps1`.
- Current import reads `F:\zky\Yuxi-main\output\ingredients_full.csv` and `F:\zky\Yuxi-main\output\products.json`.
- Current import writes `data/yuxi_import/ingredients.yuxi.json` and `data/yuxi_import/ingredient_relations.yuxi.json`.
- Current import also writes `data/yuxi_import/evidence.yuxi.json`.
- On the current Yuxi export, default import produced 46 moisturizing-related ingredients, 316 candidate relation edges, and 185 evidence records.
- Relations are product co-occurrence hints labeled as `synergy`; they are not lab-validated compatibility claims.
- Python service knowledge source overrides are now supported through `RJM_INGREDIENTS_PATH`, `RJM_RELATIONS_PATH`, and `RJM_RAW_MATERIAL_SKUS_PATH`.
- Java management in `python` mode can use these imported files indirectly by starting the Python service with the same environment variables.

## Java Python Yuxi Integration Smoke Notes

- `scripts/run_java_python_integration_smoke.ps1` now accepts `-UseYuxiKnowledge`.
- With this switch, the script refreshes `data/yuxi_import/*.json`, starts the Python HTTP service with `RJM_INGREDIENTS_PATH`, `RJM_RELATIONS_PATH`, and `RJM_EVIDENCE_PATH`, then runs Java in `python` mode.
- `JavaPythonIntegrationSmokeTests` checks normal recommendation, screening, feedback, and report calls; when `rjm.integration.expect-yuxi=true`, it also asserts that recommendation evidence IDs begin with `YUXI-`.
- This proves the current executable path: Java management API -> Python AI service -> Yuxi-imported ingredient/relation knowledge -> Java API response.

## Knowledge Status API Notes

- Python service method `FormulaAIService.knowledge_status` reports loaded ingredient count, relation count, raw material SKU count, source paths, and evidence prefix counts.
- Python HTTP endpoint added: `GET /knowledge/status`.
- Java management endpoint added: `GET /api/knowledge/status`.
- Java DTO added: `KnowledgeStatusResponse`.
- Java `PythonFormulaAiClient` delegates to Python `GET /knowledge/status`.
- Java integration smoke now calls the knowledge status endpoint; Yuxi mode also asserts `source_paths.ingredients_path` contains `ingredients.yuxi.json` and `evidence_prefix_counts.YUXI` is present.

## Evidence Traceability API Notes

- Yuxi import now creates `data/yuxi_import/evidence.yuxi.json`.
- Evidence records include `id`, `source_type`, `title`, `summary`, `source_url`, and `metadata`.
- Python service loads evidence through default `data/yuxi_import/evidence.yuxi.json` when it exists, or through `RJM_EVIDENCE_PATH`.
- Python HTTP endpoint added: `GET /evidence/{evidence_id}`.
- Java management endpoint added: `GET /api/evidence/{evidenceId}`.
- Java DTO added: `EvidenceResponse`.
- Formula engineer console now renders evidence IDs as buttons; clicking one calls `/api/evidence/{evidenceId}` and displays the source record in the output panel.
- Yuxi-mode integration smoke verifies `GET /api/evidence/YUXI-ING-GLYCERIN` returns an `ingredient_profile` source record.

## Formula Candidate Archive Notes

- Formula candidate archive store added at `prototype/rjm_formula_ai/formula_store.py`.
- Python service writes every `recommend` and `feedback_recommend` response to a JSONL archive.
- Default archive path is `data/runtime/formula_candidates.jsonl`; local demos and smoke tests can isolate it with `RJM_FORMULA_PATH`.
- Python HTTP endpoint added: `GET /formulas/{formula_id}`.
- Java management endpoint added: `GET /api/formulas/{formulaId}`.
- Java Python client and delegating service call the Python archive lookup endpoint in `python` mode.
- This lets engineer screening, experiment feedback, and procurement workflows reuse the exact candidate formula snapshot generated by AI instead of relying on transient UI state.

## Java Management Database Schema Notes

- Database draft added under `java-management/database/`.
- `schema.sql` is SQLite/H2-friendly for early validation and can later migrate to Flyway/Liquibase.
- Tables cover `formula_request`, `formula_candidate`, `formula_screening`, `experiment_feedback`, `learned_weight`, `evidence_record`, `raw_material_sku`, and `procurement_recommendation`.
- The design intentionally stores complete JSON snapshots for traceability while keeping stable query fields as ordinary columns.
- `prototype/tests/test_database_schema.py` parses the schema with in-memory SQLite and checks the core closed-loop tables and formula archive columns.

## Java Formula Archive JDBC Repository Notes

- JDBC repository added at `java-management/management-service/src/main/java/com/rjm/formulaai/management/persistence/FormulaCandidateArchiveRepository.java`.
- Tests added at `java-management/management-service/src/test/java/com/rjm/formulaai/management/persistence/FormulaCandidateArchiveRepositoryTests.java`.
- `saveRecommendation` persists one `formula_request` row and one `formula_candidate` row per recommended formula.
- `findLatestByFormulaId` returns the latest archived candidate snapshot using the same shape as `GET /api/formulas/{formulaId}`.
- `DbArchivingFormulaAiManagementService` provides an explicit `rjm.ai-service.mode=db` path. It still uses the in-memory recommendation logic, archives generated candidates through the repository, and reads formula archive lookups from the repository.
- `PersistenceConfig` creates `FormulaCandidateArchiveRepository` in `db` mode from `DataSource` and Jackson `ObjectMapper`.
- H2 test dependency added in `management-service/pom.xml`.
- H2 integration test added at `java-management/management-service/src/test/java/com/rjm/formulaai/management/DbModeH2IntegrationTests.java`.
- `schema.h2.sql` is the H2 test variant of `schema.sql`; it only changes self-increment column syntax from SQLite `autoincrement` to H2 `auto_increment`.
- `FormulaScreeningRepository` now persists and queries `formula_screening` records in `db` mode.
- `ExperimentFeedbackRepository` now persists `experiment_feedback` records and can count feedback rows by `formula_id`.
- `ExperimentFeedbackRepository.countPassingByFormulaId` counts only rows whose `result` is `pass`.
- `ExperimentFeedbackRepository.countPassingByIngredientId` counts pass rows where `ingredient_ids_json` contains a quoted ingredient id.
- `ExperimentFeedbackRepository.countPassingByIngredientPair` counts pass rows where `ingredient_ids_json` contains both quoted ingredient ids.
- `LearnedWeightRepository` persists auditable learned weights by `goal`, `target_type`, and `target_key`, with `weight`, `evidence_count`, `source`, and `calculation_note`.
- `DbArchivingFormulaAiManagementService.recommendFormulas` now applies three simple boosts before archiving: formula pass boost `overall += min(pass_count, 4) * 0.03`, ingredient pass boost capped at `0.12`, and ingredient-pair pass boost capped at `0.12` per candidate formula, then reranks by `overall` descending.
- During DB-mode recommendation, positive formula, ingredient, and ingredient-pair boosts are written to `learned_weight` once per `goal/type/key` per recommendation call, so score changes can be audited later.
- `DbArchivingFormulaAiManagementService.buildFeedbackImpactReport` now keeps the current demo report rows but replaces `feedback_count` with persisted DB counts for each returned formula id.
- `DbModeH2IntegrationTests` covers recommendation archive, archive lookup, screening write/query, experiment feedback write, feedback impact report counts, formula-level boosting, ingredient-level learned reranking, and pair-level learned reranking against H2.
- Production runtime still lacks an explicit `DataSource` configuration, so keep the current local demo on `mock` or `python` mode until that is added.
- `WebConsoleConfig` now accepts `rjm.console.location` so tests can use classpath resources while production defaults to project-level `ui/engineer-console`.

## Phase 02 Java Local DB Runtime Config Notes

- `DbLocalDataSourceConfig` creates a file-backed H2 `DataSource` when `rjm.local-db.enabled=true`.
- `application-db-local.yml` starts Java in `db` mode with local H2 storage under `data/runtime/java-db`.
- `scripts/run_java_db_local.ps1 -SmokeOnly` verifies the local DB profile and schema initialization without starting a long-running app.

## Phase 03 Learned Weight Explainability Notes

- Java management now exposes `GET /api/learning/weights` for auditable learned weights by `goal` and optional `target_type`.
- Java management now exposes `GET /api/formulas/{formulaId}/explanation` for formula-specific influences from formula, ingredient, and ingredient-pair weights.
- DB mode resolves explanations from archived formula snapshots and `learned_weight` rows, keeping only influences relevant to the formula's ingredients.
- The engineer console has `学习解释` and `学习权重` buttons and sends results to the existing JSON output panel.
- OpenAPI documents the new paths and schemas: `LearnedWeightResponse`, `LearnedWeightRow`, and `FormulaLearningExplanationResponse`.

## Formula Engineer Static Console Notes

- Static UI added under `ui/engineer-console/`.
- Main page: `ui/engineer-console/index.html`.
- The console defaults to offline sample data, so it can be opened directly without a server.
- When Java management service is running at `http://localhost:8080`, the console can call knowledge status, recommendation, screening, experiment feedback, feedback impact report, and procurement recommendation endpoints.
- The UI is intentionally static and dependency-free for early one-person development. Later it can be replaced by a Java/Vue/React management frontend while preserving the same Java API contract.
- Verified with `prototype/tests/test_engineer_console_ui.py` and `node --check ui\engineer-console\app.js`.
- Phase 04 adds `operationStatus` and `selectedFormulaSummary`, and wraps key actions through `withActionStatus` so engineers see loading/success/failure feedback without adding a frontend build system.
- Phase 05 adds `已存采购` and `申请样品` actions. `已存采购` calls `GET /api/procurement/recommendations/{formulaId}`; `申请样品` patches the current formula's first ingredient to `sample_requested`.

## Phase 05 Supplier Procurement Loop Notes

- `ProcurementRecommendationRepository` persists procurement rows to `procurement_recommendation` and saves SKU snapshots to `raw_material_sku`.
- DB mode saves procurement recommendations when `POST /api/procurement/recommend` is called.
- New API: `GET /api/procurement/recommendations/{formulaId}` returns persisted procurement rows in the existing `ProcurementRecommendationResponse` shape.
- New API: `PATCH /api/procurement/recommendations/{formulaId}/{ingredientId}/status` updates procurement status for all rows matching that formula ingredient.
- Initial status flow documented in OpenAPI: `matched`, `sample_requested`, `sample_received`, `approved`, `rejected`, `missing_supplier`.
- Mock and Python modes return empty persisted procurement lists and `updated=false`; DB mode is the authoritative path for procurement persistence.

## Local Demo Launcher and Encoding Guard Notes

- Local demo launcher added at `scripts/run_local_demo.ps1`.
- The launcher can refresh Yuxi-imported knowledge with `-UseYuxiKnowledge`, start the Python AI service, start the Java management service in `python` mode, and print the engineer console URL.
- Runtime logs are written under `data/runtime/local_demo/`.
- Python HTTP service now reads `RJM_HTTP_HOST` and `RJM_HTTP_PORT` through `server_config_from_environment`.
- Root `README.md` and `ui/engineer-console/*` Chinese copy were repaired from mojibake.
- `prototype/tests/test_engineer_console_ui.py` now rejects common mojibake fragments so encoding regressions are caught.
- `prototype/tests/test_local_demo_script.py` verifies the demo script still ties together Yuxi, Python, Java, and the static console.

## Java-hosted Engineer Console and CORS Notes

- Java console redirect controller added at `java-management/management-service/src/main/java/com/rjm/formulaai/management/controller/ConsoleController.java`.
- Spring MVC web config added at `java-management/management-service/src/main/java/com/rjm/formulaai/management/config/WebConsoleConfig.java`.
- `GET /` redirects to `/console/index.html`.
- `/console/**` serves files from the project-level `ui/engineer-console/` directory with no-store cache control for rapid iteration.
- CORS is enabled for `/api/**` from `http://localhost:8080`, `http://127.0.0.1:8080`, and `null` origins so both Java-hosted and direct file preview modes can call the management API during local development.
- Web behavior is covered by `ManagementConsoleWebTests`.

## Next Task

## Phase 06 Knowledge Governance Notes

- Yuxi import now writes `data/yuxi_import/import_batch.yuxi.json` with batch id, import timestamp, source file paths, output file paths, counts, and governance notes.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_yuxi_import.ps1` refreshed the current Yuxi import to 46 ingredients, 316 relations, 185 evidence records, and one import batch file.
- Python service now exposes `FormulaAIService.knowledge_governance()` and `GET /knowledge/governance`.
- Java management now exposes `GET /api/knowledge/governance` through `KnowledgeController`, `KnowledgeGovernanceResponse`, `PythonFormulaAiClient`, and mock/python/db service modes.
- Java database schema draft now includes `knowledge_import_batch` and `ingredient_alias`.
- Governance response includes evidence source type counts, relation type counts, relation confidence buckets, ingredient alias count, missing evidence IDs, warning count, warnings, and governance notes.
- Engineer console adds a `知识治理` action and offline governance sample.
- OpenAPI, API docs, Java management README, and the 10-phase plan now include the governance endpoint.

## Latest Verification

- `powershell -ExecutionPolicy Bypass -File .\scripts\run_yuxi_import.ps1`: passed; generated `import_batch.yuxi.json`.
- `$env:PYTHONPATH = "$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_service_api.py`: passed, 10 tests.
- `$env:PYTHONPATH = "$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_yuxi_import.py`: passed, 2 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py`: passed, 5 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py`: passed, 2 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_database_schema.py`: passed, 2 tests.
- `node --check ui\engineer-console\app.js`: passed.
- `mvn "-Dtest=ManagementApiMockMvcTests,PythonFormulaAiClientTests" test`: passed, 20 tests.

## Phase 07 Experiment Batch Management Notes

- Java database schema now includes `experiment_batch` in `schema.sql` and `schema.h2.sql`.
- Java DTOs added: `ExperimentBatchRequest`, `ExperimentBatchResponse`, and `ExperimentBatchListResponse`.
- Java repository added: `ExperimentBatchRepository`.
- New Java APIs:
  - `POST /api/experiments/batches`
  - `GET /api/experiments/batches?formula_id=...`
- DB mode persists batches through `ExperimentBatchRepository`; mock and python modes store batches in the Java management layer.
- Existing experiment feedback still records `batch_no`, so feedback is linked to batches by the batch number.
- H2 integration verifies that a planned/running batch does not create feedback rows or learned weights; learning still starts only from `experiment_feedback.result = pass`.
- Engineer console now has `创建实验批次` and `实验批次` actions.
- OpenAPI, API contract README, Java management README, database README, and the 10-phase plan now include experiment batches.

## Latest Verification

- `mvn "-Dtest=ExperimentBatchRepositoryTests,ManagementApiMockMvcTests,DbModeManagementApiTests,DbModeH2IntegrationTests" test`: passed, 18 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_database_schema.py`: passed, 2 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py`: passed, 5 tests.
- `C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py`: passed, 2 tests.
- `node --check ui\engineer-console\app.js`: passed.

## Next Task

Next recommended work: review `docs/release_acceptance.md`, run `scripts/run_release_demo.ps1`, then begin real-data pilot planning.

## Phase 08 AI Recommendation Strategy Upgrade Notes

- Python recommendation now has a strategy layer in `prototype/rjm_formula_ai/strategy.py`.
- Available strategies:
  - `baseline`: wraps the existing rule-based recommender and preserves the default recommendation path.
  - `learned_weight`: explicitly applies experiment feedback events to relation weights before ranking.
  - `exploration`: adds a small deterministic bonus for low-risk, lower-evidence candidates so future experiment design can reserve exploratory slots.
- `FormulaAIService.recommend` reads `constraints.strategy`; missing or unknown values fall back to `baseline`.
- `FormulaAIService.feedback_recommend` defaults to `learned_weight` so feedback-driven recommendation continues to express the learning loop.
- Recommendation responses now include top-level `strategy`; each formula candidate also includes its actual strategy.
- Java DTOs `FormulaRecommendationResponse` and `FormulaCandidate` now preserve the `strategy` field returned by Python mode.
- Engineer console adds a recommendation strategy selector and sends `constraints.strategy` in `/api/formulas/recommend` requests.
- OpenAPI and API contract README now document `constraints.strategy`, response strategy fields, and supported values.

## Latest Verification

- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_recommendation_strategy.py`: passed, 4 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_service_api.py`: passed, 10 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_feedback_report.py`: passed, 1 test.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_engineer_console_ui.py`: passed, 5 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py`: passed, 2 tests.
- `node --check ui\engineer-console\app.js`: passed.
- `mvn test`: passed, 58 tests, 0 failures, 0 errors, 1 skipped.

## Phase 09 Deployment and Security Notes

- `.env.example` now documents local-only defaults, ports, runtime file paths, Yuxi knowledge paths, and the optional API token gate.
- `scripts/run_prototype_stack.ps1` is the primary one-command local prototype stack launcher for Python AI, Java management, and the Java-hosted engineer console.
- `scripts/run_local_demo.ps1` remains a compatibility wrapper around `run_prototype_stack.ps1`.
- Both scripts support `-SmokeOnly`; this validates and prints the deployment configuration without starting long-running services.
- `run_prototype_stack.ps1` defaults to `127.0.0.1`; intranet exposure requires an explicit `-BindHost`.
- Java management now supports an optional `X-RJM-API-Token` gate for `/api/**` through `rjm.security.api-token.enabled=true` and `rjm.security.api-token.value=...`.
- Static console pages under `/console/**` remain accessible when the API token gate is enabled, so engineers can load the UI and configure API calls.
- CORS now allows `PATCH` for procurement status updates.
- `docs/deployment_runbook.md` records ports, runtime data/log paths, stop commands, troubleshooting steps, and the security bottom line: do not expose supplier pricing, experiment conclusions, formula percentages, or procurement state publicly.
- OpenAPI and API contract README now include `ApiTokenAuth` / `X-RJM-API-Token`.

## Latest Verification

- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_deployment_security.py`: passed, 3 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_local_demo_script.py`: passed, 2 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_java_contract_docs.py`: passed, 2 tests.
- PowerShell parser checks for `scripts\run_prototype_stack.ps1` and `scripts\run_local_demo.ps1`: passed.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_prototype_stack.ps1 -SmokeOnly`: passed.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1 -SmokeOnly`: passed.
- `mvn test`: passed, 61 tests, 0 failures, 0 errors, 1 skipped.

## Phase 10 Initial Release Acceptance Demo Notes

- `prototype/rjm_formula_ai/release_demo.py` runs the closed-loop acceptance demo and builds a business-facing summary.
- `scripts/run_release_demo.ps1` writes `data/outputs/release_demo_summary.json`.
- `docs/release_acceptance.md` explains the demo path, current capabilities, current limitations, and how to connect real RJM data next.
- Root `README.md` now presents the 10/10 initial release entry points, one-command acceptance demo, local stack startup, and verification commands.
- The acceptance summary covers the intended business loop: moisturizing formula request, 3 candidate formulas, engineer screening, passing experiment feedback, learned score delta, and procurement recommendations.
- The generated demo remains a decision-support prototype. It does not replace formulation expertise, experiments, compliance review, or safety review.

## Latest Verification

- `powershell -ExecutionPolicy Bypass -File .\scripts\run_release_demo.ps1`: passed; wrote `data/outputs/release_demo_summary.json`.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_release_acceptance.py`: passed, 3 tests.
- `$env:PYTHONPATH="$PWD\prototype"; C:\Users\m1534\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe prototype\tests\test_workflow_smoke.py`: passed, 1 test.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_java_python_integration_smoke.ps1 -UseYuxiKnowledge`: passed; refreshed Yuxi import to 46 ingredients, 316 relations, 185 evidence records, then ran Java Python integration smoke with 1 passing test.
- `mvn test`: passed, 61 tests, 0 failures, 0 errors, 1 skipped.

## Yuxi Online Graph Integration Notes

- Python now has `prototype/rjm_formula_ai/yuxi_graph_client.py` for live yuxi-know graph access.
- Enable it with `RJM_YUXI_GRAPH_ENABLED=true`; configure `RJM_YUXI_API_BASE`, optional `RJM_YUXI_KB_ID`, and optional `RJM_YUXI_API_TOKEN`.
- `HttpYuxiGateway` reads `/api/graph/list`, `/api/graph/stats`, `/api/knowledge/databases/{kb_id}/graph-build/status`, and `/api/graph/subgraph`.
- `FormulaAIService.recommend` prefers live Yuxi subgraph candidates and returns `knowledge_source=yuxi_graph_online` when recall yields usable ingredients.
- If yuxi-know is offline or the subgraph recall is empty, recommendation falls back to the local snapshot and returns `knowledge_source=snapshot_fallback`.
- `FormulaAIService.knowledge_status` returns `yuxi_graph` counts. With Yuxi running, the engineer console should show full graph counts such as 41896 entities / 409315 relationships instead of only the imported 46 / 316 snapshot.
- One-command local run with online graph mode:

```powershell
.\scripts\run_prototype_stack.ps1 -UseYuxiKnowledge -UseYuxiGraphOnline -YuxiApiBase http://127.0.0.1:5050 -JavaPort 8090 -PythonPort 8010
```

## Engineer Console UI/UX Optimization Notes

- Installed `ui-ux-pro-max` from `nextlevelbuilder/ui-ux-pro-max-skill` into `C:\Users\m1534\.codex\skills\ui-ux-pro-max`; restart Codex to pick up the skill automatically in later sessions.
- Applied `ui-ux-pro-max` rules for accessibility, 44px mobile touch targets, visible focus states, semantic design tokens, low motion, responsive layout, table overflow containment, form labels, loading/success/error feedback, and reduced-motion support.
- Reworked `ui/engineer-console/index.html` into a single-page engineer workbench: compact top status bar, left recommendation input, center candidate comparison, right selected-formula detail/actions, and bottom structured output plus collapsed raw JSON drawer.
- Rebuilt `ui/engineer-console/styles.css` around neutral biomedical/R&D design tokens, dense dashboard spacing, restrained teal/blue accents, semantic success/warning/danger states, internal table scrolling, and desktop/tablet/mobile breakpoints.
- Enhanced `ui/engineer-console/app.js` so recommendation, evidence, experiment batch, feedback impact, learning weights/explanation, procurement, saved procurement, and status responses render as structured cards/tables while preserving raw JSON in `actionOutput`.
- Preserved existing static/no-build implementation, direct file offline sample mode, Java `/console/**` hosting, API paths, snake_case payloads, `operationStatus`, `selectedFormulaSummary`, `withActionStatus`, and existing business buttons.
- Added optional `apiToken` password field for `X-RJM-API-Token`; token is only sent in request headers and is not written to debug JSON.
- Browser verification used a temporary local static server at `http://127.0.0.1:8765/index.html`; desktop and 390px mobile checks showed three offline candidates, selected formula details, collapsed debug drawer, readable non-JSON API fallback, and no page-level horizontal overflow. Temporary process was stopped.

## Latest Verification

- `$env:PYTHONPATH="$PWD\prototype"; python prototype\tests\test_engineer_console_ui.py`: passed, 6 tests.
- `node --check ui\engineer-console\app.js`: passed.
- `cd java-management\management-service; mvn "-Dtest=ManagementConsoleWebTests,ManagementApiMockMvcTests" test`: passed, 14 tests.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_prototype_stack.ps1 -SmokeOnly`: passed; printed Python health URL, Java health URL, console URL, runtime logs, token status, and Yuxi graph setting.
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_release_demo.ps1`: passed; wrote `data/outputs/release_demo_summary.json`.
- `cd java-management\management-service; mvn test`: passed, 61 tests run, 0 failures, 0 errors, 1 skipped.
