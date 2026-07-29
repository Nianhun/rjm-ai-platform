import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class DatabaseSchemaTest(unittest.TestCase):
    def test_schema_defines_closed_loop_tables(self):
        schema_path = ROOT / "infrastructure" / "database" / "java-management" / "schema.sql"
        schema = schema_path.read_text(encoding="utf-8")

        conn = sqlite3.connect(":memory:")
        conn.executescript(schema)

        tables = {
            row[0]
            for row in conn.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
        }
        expected_tables = {
            "formula_request",
            "formula_candidate",
            "formula_screening",
            "experiment_feedback",
            "raw_material_sku",
            "procurement_recommendation",
            "evidence_record",
            "learned_weight",
            "knowledge_import_batch",
            "ingredient_alias",
            "experiment_batch",
        }
        self.assertTrue(expected_tables.issubset(tables))

        candidate_columns = {
            row[1]
            for row in conn.execute("pragma table_info(formula_candidate)").fetchall()
        }
        self.assertTrue(
            {
                "formula_id",
                "request_id",
                "goal",
                "status",
                "formula_json",
                "score_total",
                "created_at",
            }.issubset(candidate_columns)
        )

    def test_schema_readme_names_persistence_path(self):
        readme_path = ROOT / "infrastructure" / "database" / "java-management" / "README.md"
        text = readme_path.read_text(encoding="utf-8")

        self.assertIn("schema.sql", text)
        self.assertIn("schema.h2.sql", text)
        self.assertIn("SQLite", text)
        self.assertIn("PostgreSQL", text)


if __name__ == "__main__":
    unittest.main()
