import unittest

from rjm_formula_ai.models import IngredientRelation
from rjm_formula_ai.yuxi_graph_client import YuxiGraphClient


class FakeYuxiGateway:
    def list_graphs(self):
        return [
            {
                "id": "kb-cosmetic",
                "name": "化妆品原料知识库",
                "type": "milvus",
            }
        ]

    def get_graph_stats(self, kb_id):
        self.kb_id = kb_id
        return {
            "total_nodes": 55219,
            "total_edges": 409315,
            "entity_types": [{"type": "Ingredient", "count": 41896}],
        }

    def get_graph_build_status(self, kb_id):
        return {
            "total_chunks": 13323,
            "indexed_chunks": 13323,
            "pending_chunks": 0,
            "entity_count": 41896,
            "relationship_count": 409315,
        }

    def get_subgraph(self, kb_id, keyword, max_depth, max_nodes, exclude_chunk):
        return {
            "nodes": [
                {
                    "id": "ent-glycerin",
                    "type": "Entity",
                    "label": "Ingredient",
                    "name": "Glycerin",
                    "properties": {
                        "entity_id": "ent-glycerin",
                        "name": "Glycerin",
                        "label": "Ingredient",
                        "description": "Humectant moisturizer",
                    },
                },
                {
                    "id": "ent-panthenol",
                    "type": "Entity",
                    "label": "Ingredient",
                    "name": "Panthenol",
                    "properties": {
                        "entity_id": "ent-panthenol",
                        "name": "Panthenol",
                        "label": "Ingredient",
                        "description": "Moisturizing barrier support",
                    },
                },
            ],
            "edges": [
                {
                    "id": "rel-1",
                    "source_id": "ent-glycerin",
                    "target_id": "ent-panthenol",
                    "type": "RELATION",
                    "properties": {"relation_type": "synergy", "content": "co-occurs in moisturizing formulas"},
                }
            ],
        }


class YuxiGraphClientTest(unittest.TestCase):
    def test_status_uses_full_yuxi_graph_counts(self):
        client = YuxiGraphClient(FakeYuxiGateway())

        status = client.status()

        self.assertTrue(status["online"])
        self.assertEqual(status["kb_id"], "kb-cosmetic")
        self.assertEqual(status["entity_count"], 41896)
        self.assertEqual(status["relationship_count"], 409315)
        self.assertEqual(status["total_chunks"], 13323)
        self.assertEqual(status["raw"]["total_edges"], 409315)

    def test_recall_formula_subgraph_maps_entities_and_relations(self):
        client = YuxiGraphClient(FakeYuxiGateway())

        knowledge = client.recall_formula_knowledge("保湿", max_ingredients=10)

        self.assertEqual([item.id for item in knowledge.ingredients], ["YUXI-ENT-GLYCERIN", "YUXI-ENT-PANTHENOL"])
        self.assertEqual(knowledge.ingredients[0].functions, ["保湿"])
        self.assertEqual(len(knowledge.relations), 1)
        self.assertIsInstance(knowledge.relations[0], IngredientRelation)
        self.assertEqual(knowledge.relations[0].relation_type, "synergy")


if __name__ == "__main__":
    unittest.main()
