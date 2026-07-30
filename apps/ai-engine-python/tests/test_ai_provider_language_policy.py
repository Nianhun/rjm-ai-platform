import unittest

from rjm_formula_ai.ai_provider import OpenAICompatibleFormulaAnalyzer, normalize_ai_chat
from rjm_formula_ai.models import FormulaRequest, Ingredient, IngredientRelation, UsageRange
from rjm_formula_ai.yuxi_graph_client import FormulaKnowledge


def _knowledge():
    glycerin = Ingredient(
        id="YUXI-GLYCERIN",
        name_cn="Glycerin",
        name_en="Glycerin",
        inci_name="GLYCERIN",
        category="humectant",
        functions=["moisturizing"],
        properties={},
        usage_range=UsageRange(min_percent=1.0, max_percent=5.0, typical_percent=3.0),
        regulatory_limits=[],
        risk_tags=[],
        evidence_ids=["YUXI-GRAPH-GLYCERIN"],
    )
    panthenol = Ingredient(
        id="YUXI-PANTHENOL",
        name_cn="Panthenol",
        name_en="Panthenol",
        inci_name="PANTHENOL",
        category="active",
        functions=["barrier support"],
        properties={},
        usage_range=UsageRange(min_percent=0.5, max_percent=2.0, typical_percent=1.0),
        regulatory_limits=[],
        risk_tags=[],
        evidence_ids=["YUXI-GRAPH-PANTHENOL"],
    )
    return FormulaKnowledge(
        ingredients=[glycerin, panthenol],
        relations=[
            IngredientRelation(
                id="YUXI-REL-1",
                source_ingredient_id="YUXI-GLYCERIN",
                target_ingredient_id="YUXI-PANTHENOL",
                relation_type="synergy",
                description="co-occurs in moisturizing formulas",
                strength=0.7,
                feedback_weight=0.0,
                evidence_ids=["YUXI-GRAPH-GLYCERIN"],
            )
        ],
        evidence_catalog=[
            {
                "id": "YUXI-GRAPH-GLYCERIN",
                "summary": "Glycerin supports moisturization.",
            }
        ],
        graph_stats={"entity_count": 41896, "relationship_count": 409315},
    )


class CapturingAnalyzer(OpenAICompatibleFormulaAnalyzer):
    def __init__(self):
        super().__init__("http://example.test", "token", "deepseek-v4flash")
        self.payloads = []

    def _post_json(self, path, payload):
        self.payloads.append(payload)
        if "Generate evidence-backed formula" in payload["messages"][1]["content"]:
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "formulas": [
                                {
                                  "id": "F-001",
                                  "ingredients": [
                                    {
                                      "ingredient_id": "YUXI-GLYCERIN",
                                      "role": "保湿剂",
                                      "suggested_percent_min": 1,
                                      "suggested_percent_max": 3
                                    }
                                  ],
                                  "recommendation_reason": "Glycerin 作为基础保湿剂，适合当前目标。",
                                  "risk_notes": ["需要验证肤感和稳定性。"],
                                  "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
                                  "score": {
                                    "efficacy": 0.8,
                                    "stability": 0.7,
                                    "skin_feel": 0.7,
                                    "cost": 0.8,
                                    "supply": 0.9,
                                    "overall": 0.78
                                  }
                                }
                              ]
                            }
                            """
                        }
                    }
                ]
            }
        return {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                          "answer": "Glycerin 可以保留英文原料名，并用中文解释使用理由。",
                          "follow_up_questions": ["是否需要限制肤感黏腻度？"],
                          "ingredient_ids": ["YUXI-GLYCERIN"],
                          "evidence_ids": ["YUXI-GRAPH-GLYCERIN"]
                        }
                        """
                    }
                }
            ]
        }


class RetryLanguageAnalyzer(CapturingAnalyzer):
    def _post_json(self, path, payload):
        self.payloads.append(payload)
        if len(self.payloads) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "formulas": [
                                {
                                  "id": "F-001",
                                  "ingredients": [
                                    {
                                      "ingredient_id": "YUXI-GLYCERIN",
                                      "role": "humectant",
                                      "suggested_percent_min": 1,
                                      "suggested_percent_max": 3
                                    }
                                  ],
                                  "recommendation_reason": "Glycerin is a good moisturizing anchor.",
                                  "risk_notes": ["Check skin feel."],
                                  "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
                                  "score": {
                                    "efficacy": 0.8,
                                    "stability": 0.7,
                                    "skin_feel": 0.7,
                                    "cost": 0.8,
                                    "supply": 0.9,
                                    "overall": 0.78
                                  }
                                }
                              ]
                            }
                            """
                        }
                    }
                ]
            }
        return {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                          "formulas": [
                            {
                              "id": "F-001",
                              "ingredients": [
                                {
                                  "ingredient_id": "YUXI-GLYCERIN",
                                  "role": "保湿剂",
                                  "suggested_percent_min": 1,
                                  "suggested_percent_max": 3
                                }
                              ],
                              "recommendation_reason": "Glycerin 作为基础保湿剂，适合当前目标。",
                              "risk_notes": ["需要验证肤感和稳定性。"],
                              "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
                              "score": {
                                "efficacy": 0.8,
                                "stability": 0.7,
                                "skin_feel": 0.7,
                                "cost": 0.8,
                                "supply": 0.9,
                                "overall": 0.78
                              }
                            }
                          ]
                        }
                        """
                    }
                }
            ]
        }


class RetryRoleLanguageAnalyzer(RetryLanguageAnalyzer):
    def _post_json(self, path, payload):
        self.payloads.append(payload)
        if len(self.payloads) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "formulas": [
                                {
                                  "id": "F-001",
                                  "ingredients": [
                                    {
                                      "ingredient_id": "YUXI-GLYCERIN",
                                      "role": "humectant",
                                      "suggested_percent_min": 1,
                                      "suggested_percent_max": 3
                                    }
                                  ],
                                  "recommendation_reason": "Glycerin 作为基础保湿剂，适合当前目标。",
                                  "risk_notes": ["需要验证肤感和稳定性。"],
                                  "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
                                  "score": {
                                    "efficacy": 0.8,
                                    "stability": 0.7,
                                    "skin_feel": 0.7,
                                    "cost": 0.8,
                                    "supply": 0.9,
                                    "overall": 0.78
                                  }
                                }
                              ]
                            }
                            """
                        }
                    }
                ]
            }
        return {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                          "formulas": [
                            {
                              "id": "F-001",
                              "ingredients": [
                                {
                                  "ingredient_id": "YUXI-GLYCERIN",
                                  "role": "保湿剂",
                                  "suggested_percent_min": 1,
                                  "suggested_percent_max": 3
                                }
                              ],
                              "recommendation_reason": "Glycerin 作为基础保湿剂，适合当前目标。",
                              "risk_notes": ["需要验证肤感和稳定性。"],
                              "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
                              "score": {
                                "efficacy": 0.8,
                                "stability": 0.7,
                                "skin_feel": 0.7,
                                "cost": 0.8,
                                "supply": 0.9,
                                "overall": 0.78
                              }
                            }
                          ]
                        }
                        """
                    }
                }
            ]
        }


class AiProviderLanguagePolicyTest(unittest.TestCase):
    def test_recommendation_prompt_requires_chinese_prose_and_original_ingredient_names(self):
        analyzer = CapturingAnalyzer()

        analyzer.recommend(
            FormulaRequest(id="REQ-1", goal="保湿", dosage_form="乳液", constraints={}),
            _knowledge(),
            feedback_events=[],
            strategy_name="knowledge_graph_ai",
        )

        system_prompt = analyzer.payloads[-1]["messages"][0]["content"]
        output_contract = analyzer.payloads[-1]["messages"][1]["content"]
        self.assertIn("Simplified Chinese", system_prompt)
        self.assertIn("ingredient names, INCI names, ingredient IDs, evidence IDs, and formula IDs", system_prompt)
        self.assertIn("recommendation_reason", output_contract)
        self.assertIn("risk_notes", output_contract)
        self.assertIn("Simplified Chinese", output_contract)

    def test_chat_prompt_requires_chinese_answer_and_follow_ups(self):
        analyzer = CapturingAnalyzer()

        analyzer.chat("这个组合适合敏感肌吗？", _knowledge())

        system_prompt = analyzer.payloads[-1]["messages"][0]["content"]
        output_contract = analyzer.payloads[-1]["messages"][1]["content"]
        self.assertIn("Simplified Chinese", system_prompt)
        self.assertIn("ingredient names, INCI names, ingredient IDs, evidence IDs, and formula IDs", system_prompt)
        self.assertIn("answer", output_contract)
        self.assertIn("follow_up_questions", output_contract)
        self.assertIn("Simplified Chinese", output_contract)

    def test_chat_preserves_structured_formula_graph_fields(self):
        result = normalize_ai_chat(
            {
                "answer": "建议使用一个美白精华配方，并按功效分类展示。",
                "formula_ingredients": [
                    {
                        "ingredient_id": "YUXI-GLYCERIN",
                        "name": "Glycerin",
                        "concentration": "5%",
                        "function_group": "保湿",
                        "core_effect": "补水",
                    }
                ],
                "function_groups": [{"name": "保湿", "ingredient_ids": ["YUXI-GLYCERIN"]}],
                "relation_edges": [{"source": "保湿", "target": "YUXI-GLYCERIN", "label": "功效证据"}],
                "core_path": ["保湿：Glycerin 补水"],
                "ingredient_ids": ["YUXI-GLYCERIN"],
                "evidence_ids": ["YUXI-GRAPH-GLYCERIN"],
            },
            ["YUXI-GLYCERIN"],
            ["YUXI-GRAPH-GLYCERIN"],
        )

        self.assertEqual(result["formula_ingredients"][0]["name"], "Glycerin")
        self.assertEqual(result["function_groups"][0]["name"], "保湿")
        self.assertEqual(result["relation_edges"][0]["label"], "功效证据")
        self.assertEqual(result["core_path"], ["保湿：Glycerin 补水"])

    def test_recommendation_retries_once_when_explanatory_text_is_english(self):
        analyzer = RetryLanguageAnalyzer()

        formulas = analyzer.recommend(
            FormulaRequest(id="REQ-1", goal="保湿", dosage_form="乳液", constraints={}),
            _knowledge(),
            feedback_events=[],
            strategy_name="knowledge_graph_ai",
        )

        self.assertEqual(len(analyzer.payloads), 2)
        self.assertIn("All explanatory prose must be Simplified Chinese", analyzer.payloads[-1]["messages"][-1]["content"])
        self.assertEqual(formulas[0]["recommendation_reason"], "Glycerin 作为基础保湿剂，适合当前目标。")

    def test_recommendation_retries_once_when_role_label_is_english(self):
        analyzer = RetryRoleLanguageAnalyzer()

        formulas = analyzer.recommend(
            FormulaRequest(id="REQ-1", goal="保湿", dosage_form="乳液", constraints={}),
            _knowledge(),
            feedback_events=[],
            strategy_name="knowledge_graph_ai",
        )

        self.assertEqual(len(analyzer.payloads), 2)
        self.assertEqual(formulas[0]["ingredients"][0]["role"], "保湿剂")


if __name__ == "__main__":
    unittest.main()
