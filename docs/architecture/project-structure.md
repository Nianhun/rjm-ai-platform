# Project Structure

## Why The Repository Is Split This Way

This repository is a small monorepo with three runnable projects and several shared/supporting areas. Only code that exists and has a real entry point is placed under `apps/`; planned services such as literature, patent, equipment, and compliance services are not scaffolded until they have implementation.

## Runnable Projects

- `apps/ai-engine-python/` owns the Python AI engine, local HTTP adapter, recommendation workflow, feedback learning, Yuxi import/graph integration, and Python tests.
- `apps/java-admin-service/` owns the Spring Boot management API, DTOs, controllers, service seams, Python HTTP client adapter, and JDBC persistence adapters.
- `apps/engineer-console/` owns the static engineer workbench UI served by the Java service at `/console/**`.

## Shared And Infrastructure Areas

- `shared/api-contracts/java-management/` contains the OpenAPI contract shared by Java, Python, docs, and tests.
- `shared/schemas/` contains JSON Schemas for sample and exchange data.
- `infrastructure/database/java-management/` contains SQL schema drafts for Java DB mode.
- `data/` contains sample data, Yuxi import outputs, runtime state, and generated reports.
- `scripts/` contains executable wrappers grouped by purpose.

## Dependency Direction

Allowed:

```text
engineer-console -> java-admin-service -> ai-engine-python
java-admin-service -> shared/api-contracts
ai-engine-python -> shared/schemas, data
java-admin-service -> infrastructure/database
scripts -> apps, shared, infrastructure, data
```

Forbidden:

```text
ai-engine-python -> java-admin-service internals
shared -> apps
infrastructure -> apps business code
engineer-console -> ai-engine-python directly in production
```

## Compatibility

The old paths are preserved as compatibility entry points, either by wrapper scripts or directory links. They are not the source of truth for new development.

## Where New Code Goes

- New Python AI business use cases: `apps/ai-engine-python/src/rjm_formula_ai/`.
- New Java API endpoints: controller/service/dto packages under `apps/java-admin-service/src/main/java/.../management/`.
- New persistence schema work: `infrastructure/database/java-management/`.
- New API contracts: `shared/api-contracts/`.
- New JSON schemas: `shared/schemas/`.
- New operational scripts: the appropriate `scripts/demo`, `scripts/development`, `scripts/integration`, or `scripts/database` folder, plus a root wrapper only if backward compatibility matters.
