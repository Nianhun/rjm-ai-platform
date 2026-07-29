import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rjm_formula_ai.yuxi_import import import_yuxi_output


ROOT = Path(__file__).resolve().parents[3]


class YuxiImportTest(unittest.TestCase):
    def test_imports_moisturizing_ingredients_relations_and_evidence_catalog(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "yuxi-output"
            output.mkdir()
            ingredients_path = output / "ingredients_full.csv"
            products_path = output / "products.json"

            with ingredients_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "ingredient_name",
                        "ingredient_url",
                        "what_it_does",
                        "all_functions",
                        "cas_number",
                        "ec_number",
                        "ph_eur_name",
                        "iupac_name",
                        "sccs_opinions",
                        "description",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "ingredient_name": "Glycerin",
                        "ingredient_url": "https://incidecoder.com/ingredients/glycerin",
                        "what_it_does": "moisturizer/humectant",
                        "all_functions": "humectant, skin conditioning",
                        "description": "Classic moisturizing ingredient.",
                    }
                )
                writer.writerow(
                    {
                        "ingredient_name": "Panthenol",
                        "ingredient_url": "https://incidecoder.com/ingredients/panthenol",
                        "what_it_does": "soothing, moisturizer",
                        "all_functions": "skin conditioning",
                        "description": "Supports skin barrier.",
                    }
                )
                writer.writerow(
                    {
                        "ingredient_name": "Fragrance",
                        "ingredient_url": "https://incidecoder.com/ingredients/fragrance",
                        "what_it_does": "perfuming",
                        "all_functions": "perfuming",
                        "description": "Perfume ingredient.",
                    }
                )

            products_path.write_text(
                json.dumps(
                    [
                        {
                            "product_name": "Moisture Cream",
                            "product_url": "https://example.test/products/moisture-cream",
                            "ingredients": [
                                {"ingredient_name": "Glycerin", "ingredient_url": "https://incidecoder.com/ingredients/glycerin"},
                                {"ingredient_name": "Panthenol", "ingredient_url": "https://incidecoder.com/ingredients/panthenol"},
                                {"ingredient_name": "Fragrance", "ingredient_url": "https://incidecoder.com/ingredients/fragrance"},
                            ],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            result = import_yuxi_output(output, root / "rjm")

            self.assertEqual(result["ingredient_count"], 2)
            self.assertEqual(result["relation_count"], 1)
            self.assertEqual(result["evidence_count"], 3)
            self.assertTrue(result["batch_path"].endswith("import_batch.yuxi.json"))

            ingredients = json.loads((root / "rjm" / "ingredients.yuxi.json").read_text(encoding="utf-8"))
            relations = json.loads((root / "rjm" / "ingredient_relations.yuxi.json").read_text(encoding="utf-8"))
            evidence = json.loads((root / "rjm" / "evidence.yuxi.json").read_text(encoding="utf-8"))
            batch = json.loads((root / "rjm" / "import_batch.yuxi.json").read_text(encoding="utf-8"))

            self.assertEqual([item["id"] for item in ingredients], ["ING-GLYCERIN", "ING-PANTHENOL"])
            self.assertIn("humectant", ingredients[0]["functions"])
            self.assertEqual(relations[0]["source_ingredient_id"], "ING-GLYCERIN")
            self.assertEqual(relations[0]["target_ingredient_id"], "ING-PANTHENOL")
            self.assertEqual(relations[0]["relation_type"], "synergy")
            self.assertEqual(relations[0]["evidence_ids"], ["YUXI-PRODUCT-MOISTURE-CREAM"])

            evidence_by_id = {item["id"]: item for item in evidence}
            self.assertEqual(evidence_by_id["YUXI-ING-GLYCERIN"]["source_type"], "ingredient_profile")
            self.assertEqual(
                evidence_by_id["YUXI-ING-GLYCERIN"]["source_url"],
                "https://incidecoder.com/ingredients/glycerin",
            )
            self.assertEqual(evidence_by_id["YUXI-PRODUCT-MOISTURE-CREAM"]["source_type"], "product_cooccurrence")
            self.assertEqual(
                evidence_by_id["YUXI-PRODUCT-MOISTURE-CREAM"]["source_url"],
                "https://example.test/products/moisture-cream",
            )
            self.assertEqual(
                evidence_by_id["YUXI-PRODUCT-MOISTURE-CREAM"]["metadata"]["matched_ingredient_ids"],
                ["ING-GLYCERIN", "ING-PANTHENOL"],
            )
            self.assertEqual(batch["counts"]["ingredient_count"], 2)
            self.assertEqual(batch["counts"]["relation_count"], 1)
            self.assertIn("ingredients_full_csv", batch["source_files"])
            self.assertIn("governance_notes", batch)

    def test_yuxi_import_entrypoints_exist(self):
        self.assertTrue((ROOT / "scripts" / "run_yuxi_import.ps1").exists())
        self.assertTrue((ROOT / "data" / "yuxi_import" / "ingredients.yuxi.json").exists())
        self.assertTrue((ROOT / "data" / "yuxi_import" / "ingredient_relations.yuxi.json").exists())
        self.assertTrue((ROOT / "data" / "yuxi_import" / "evidence.yuxi.json").exists())
        self.assertTrue((ROOT / "data" / "yuxi_import" / "import_batch.yuxi.json").exists())


if __name__ == "__main__":
    unittest.main()

