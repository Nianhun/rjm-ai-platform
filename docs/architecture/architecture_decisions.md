# Architecture Decisions

## ADR-001: Use Yuxi as knowledge and agent base

Decision: Reuse `F:\zky\Yuxi-main` for knowledge base, RAG, graph, and agent orchestration.

Reason: Yuxi already provides document parsing, Milvus retrieval, Neo4j graph support, and LangGraph agents.

Consequence: RJM-specific prototype code stays in `F:\zky\RJM`; Yuxi changes require explicit task approval.

## ADR-002: Use Python before Java

Decision: Build the formula recommendation loop in Python first.

Reason: The core uncertainty is AI extraction, recommendation, and feedback learning, not enterprise CRUD.

Consequence: Java management system starts after the Python loop proves value.

## ADR-003: Keep human approval in the loop

Decision: Formula recommendations are draft references for engineers.

Reason: Cosmetic and biomedical formulation decisions require expert review, experiment, and compliance checks.

Consequence: Every formula candidate has a status and screening record.

## ADR-004: Keep the web adapter replaceable

Decision: Implement the first local API as a zero-dependency HTTP adapter and keep business logic in `FormulaAIService`.

Reason: FastAPI and uvicorn were not available in the current runtime, and dependency installation was blocked by the environment proxy.

Consequence: Later FastAPI work should create a thin adapter over `FormulaAIService` without changing recommendation or feedback logic.
