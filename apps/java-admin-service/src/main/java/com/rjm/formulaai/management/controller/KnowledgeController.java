package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class KnowledgeController {
    private final FormulaAiManagementService service;

    public KnowledgeController(FormulaAiManagementService service) {
        this.service = service;
    }

    @GetMapping("/api/knowledge/status")
    public KnowledgeStatusResponse getKnowledgeStatus() {
        return service.getKnowledgeStatus();
    }

    @GetMapping("/api/knowledge/entity-names")
    public Map getYuxiEntityNames() {
        return service.getYuxiEntityNames();
    }

    @GetMapping("/api/knowledge/governance")
    public KnowledgeGovernanceResponse getKnowledgeGovernance() {
        return service.getKnowledgeGovernance();
    }

    @GetMapping("/api/knowledge/elements/{elementId}/graph")
    public Map getElementGraph(@PathVariable String elementId) {
        return service.getElementGraph(elementId);
    }
}
