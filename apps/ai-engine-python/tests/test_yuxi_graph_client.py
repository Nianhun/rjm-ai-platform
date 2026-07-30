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
        self.last_subgraph_request = {
            "kb_id": kb_id,
            "keyword": keyword,
            "max_depth": max_depth,
            "max_nodes": max_nodes,
            "exclude_chunk": exclude_chunk,
        }
        if keyword == "Phenoxyethanol":
            return {
                "nodes": [
                    {
                        "id": "prod-mask",
                        "type": "Entity",
                        "label": "Product",
                        "name": "Studio Ready Hot Perfecting Cream",
                        "properties": {
                            "entity_id": "prod-mask",
                            "name": "Studio Ready Hot Perfecting Cream",
                            "label": "Product",
                        },
                    },
                    {
                        "id": "ent-phenoxyethanol",
                        "type": "Entity",
                        "label": "Ingredient",
                        "name": "Phenoxyethanol",
                        "properties": {
                            "entity_id": "ent-phenoxyethanol",
                            "name": "Phenoxyethanol",
                            "label": "Ingredient",
                        },
                    },
                ],
                "edges": [
                    {
                        "id": "contains-1",
                        "source_id": "prod-mask",
                        "target_id": "ent-phenoxyethanol",
                        "type": "CONTAINS",
                        "properties": {"relation_type": "CONTAINS"},
                    }
                ],
            }
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

    def list_entities(self, kb_id, label="Ingredient", limit=100000):
        return [
            {"entity_id": "0e2dbaf04e4ebaf378f5866fc0887323", "name": "Water", "label": "Ingredient"},
            {"entity_id": "9e0989ede09e665c91365eeb437a3f98", "name": "Glycerin", "label": "Ingredient"},
            {"entity_id": "dba175d813da6ec2320e668f799557e0", "name": "Phenoxyethanol", "label": "Ingredient"},
        ]


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

    def test_entity_name_map_uses_yuxi_entity_names(self):
        client = YuxiGraphClient(FakeYuxiGateway())

        names = client.entity_name_map()

        self.assertEqual(names["YUXI-0E2DBAF04E4EBAF378F5866FC0887323"], "Water")
        self.assertEqual(names["YUXI-9E0989EDE09E665C91365EEB437A3F98"], "Glycerin")

    def test_chat_recall_uses_mentioned_entity_and_keeps_product_edges(self):
        gateway = FakeYuxiGateway()
        client = YuxiGraphClient(gateway)

        knowledge = client.recall_chat_knowledge("Phenoxyethanol 是什么？", max_nodes=10)

        self.assertEqual(gateway.last_subgraph_request["keyword"], "Phenoxyethanol")
        self.assertEqual(gateway.last_subgraph_request["max_depth"], 1)
        self.assertTrue(gateway.last_subgraph_request["exclude_chunk"])
        labels = [item.name_en for item in knowledge.ingredients]
        self.assertIn("Phenoxyethanol", labels)
        self.assertIn("Studio Ready Hot Perfecting Cream", labels)
        self.assertEqual(len(knowledge.relations), 1)
        self.assertEqual(knowledge.relations[0].relation_type, "CONTAINS")


if __name__ == "__main__":
    unittest.main()
