package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.FormulaLearningExplanationResponse;
import com.rjm.formulaai.management.dto.LearnedWeightResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LearningController {
    private final FormulaAiManagementService service;

    public LearningController(FormulaAiManagementService service) {
        this.service = service;
    }

    @GetMapping("/api/learning/weights")
    public LearnedWeightResponse listLearnedWeights(
            @RequestParam("goal") String goal,
            @RequestParam("target_type") String targetType) {
        return service.listLearnedWeights(goal, targetType);
    }

    @GetMapping("/api/formulas/{formulaId}/explanation")
    public FormulaLearningExplanationResponse explainFormulaLearning(
            @PathVariable String formulaId,
            @RequestParam("goal") String goal) {
        return service.explainFormulaLearning(formulaId, goal);
    }
}
