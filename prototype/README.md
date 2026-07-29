# Compatibility Path

The Python AI engine now lives in `apps/ai-engine-python/`.

This directory is kept only as a compatibility entry point:

- `prototype/rjm_formula_ai` links to `apps/ai-engine-python/src/rjm_formula_ai`
- `prototype/tests` links to `apps/ai-engine-python/tests`

Legacy commands that set `PYTHONPATH=prototype` continue to work.
