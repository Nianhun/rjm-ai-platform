# Yuxi Knowledge Base Source Data

This directory preserves the source artifacts used to seed the Yuxi knowledge base and knowledge graph for the RJM platform.

Use these files after starting `apps/yuxi-knowledge-platform`:

- `products_knowledge.md`: consolidated knowledge-base document for import.
- `products.ndjson`, `products.json`, `products.csv`: product-level structured source data.
- `ingredients_full.csv`, `ingredients_full.xlsx`: ingredient source data.
- `all_product_urls.csv`, `product_urls.csv`, `ingredient_urls.csv`: crawl/source URL lists.
- `import_to_kb.py`: helper script from the original Yuxi output folder for importing source data into Yuxi.
- `crawl_data.py`, `extract_data.ps1`: source collection and extraction helpers.

Runtime database volumes from Yuxi, such as PostgreSQL, Milvus, Neo4j, MinIO, and Redis data directories, are intentionally not committed. Recreate those services with Yuxi Docker Compose and import this source data into the running knowledge base.
