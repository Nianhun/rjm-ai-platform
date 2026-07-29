# Project Structure

This project keeps the runnable application paths stable while separating source, interfaces, data, documentation, and tooling.

## Runtime Entry Points

- `prototype/` - Python AI prototype and Python tests.
- `java-management/management-service/` - Spring Boot management service.
- `ui/engineer-console/` - engineer console static UI.
- `scripts/` - root-level PowerShell runners for demos, smoke tests, and local services.

## Architecture Layers

- `prototype/rjm_formula_ai/` - AI application logic, recommendation workflow, feedback learning, procurement matching, and Python HTTP adapter.
- `java-management/management-service/src/main/java/.../controller/` - Java presentation layer for management APIs.
- `java-management/management-service/src/main/java/.../service/` - Java application/service seam.
- `java-management/management-service/src/main/java/.../persistence/` - Java infrastructure adapters for JDBC persistence.
- `java-management/management-service/src/main/java/.../client/` - Java infrastructure adapter for the Python AI HTTP service.
- `java-management/management-service/src/main/java/.../dto/` - Java transport models that mirror the OpenAPI contract.

## Interfaces And Contracts

- `java-management/api-contract/` - OpenAPI contract for Java/Python management integration.
- `schemas/` - JSON schemas for formula, ingredient, feedback, relation, and procurement sample data.
- `java-management/database/` - database schema drafts and persistence notes.

## Data

- `data/samples/` - small local sample data used by demos and tests.
- `data/yuxi_import/` - converted Yuxi knowledge exports.
- `data/runtime/` - local runtime state and logs.
- `data/outputs/` - generated demo and report outputs.

## Documentation

- `docs/` - product, architecture, API, deployment, handoff, and release documentation.
- `docs/implementation_10_phase/` - phase-by-phase implementation notes.
- `docs/source-materials/` - original Word/PDF source and reference documents.
- `docs/superpowers/` - planning artifacts created during prior development sessions.

## Tooling

- `tools/document-generation/` - standalone document generation utilities.

## Current Reorganization Policy

The first cleanup pass intentionally does not move `prototype/`, `java-management/`, `data/`, `schemas/`, `scripts/`, or `ui/` because scripts, tests, and documentation already use those paths as stable entry points. A later deeper refactor can split Python and Java internals further by domain/application/infrastructure layers once the tests are updated alongside it.
