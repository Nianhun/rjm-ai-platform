# Java Admin Service

## Responsibility

Spring Boot management API for formula recommendation workflows, experiment feedback, procurement, learning explanations, evidence lookup, and static console hosting.

## Tech Stack

- Java 8
- Spring Boot 2.7.18
- Maven
- H2/JDBC for local DB mode

## Structure

```text
src/main/java/.../controller     HTTP presentation layer
src/main/java/.../service        Application service seam
src/main/java/.../client         Python AI HTTP adapter
src/main/java/.../persistence    JDBC infrastructure adapters
src/main/java/.../dto            Transport models
src/main/resources               Spring configuration
src/test                         Java tests
```

## Environment And Config

- `rjm.ai-service.mode`: `mock`, `python`, or `db`
- `rjm.python-ai.base-url`: Python AI service URL
- `rjm.security.api-token.enabled`: optional token gate
- `rjm.security.api-token.value`: optional local/intranet token
- `rjm.local-db.*`: H2 local DB settings
- `rjm.console.location`: optional static console override

## Start

```powershell
cd F:\zky\RJM\apps\java-admin-service
mvn spring-boot:run
```

Python-backed mode:

```powershell
cd F:\zky\RJM\apps\java-admin-service
mvn spring-boot:run -Dspring-boot.run.arguments="--rjm.ai-service.mode=python --rjm.python-ai.base-url=http://127.0.0.1:8000"
```

Legacy path remains available:

```powershell
cd F:\zky\RJM\java-management\management-service
mvn test
```

## Tests

```powershell
cd F:\zky\RJM\apps\java-admin-service
mvn test
```

Java-to-Python integration smoke:

```powershell
powershell -ExecutionPolicy Bypass -File F:\zky\RJM\scripts\run_java_python_integration_smoke.ps1
```

## Contracts And Database

- OpenAPI: `shared/api-contracts/java-management/openapi.json`
- SQL schema: `infrastructure/database/java-management/schema.sql`
- H2 schema: `infrastructure/database/java-management/schema.h2.sql`

## Dependent Services

- Python AI service when `rjm.ai-service.mode=python`
- Local H2/JDBC when `rjm.ai-service.mode=db` or `db-local` profile is used
- Engineer console files under `apps/engineer-console`

Key Python mapping: `FormulaController.recommendFormulas` delegates to `FormulaAIService.recommend` through the Python adapter when the service runs in `python` mode.
