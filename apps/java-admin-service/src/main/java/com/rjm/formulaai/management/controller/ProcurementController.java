package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.persistence.ProcurementStatusUpdateResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import java.util.Map;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProcurementController {
    private final FormulaAiManagementService service;

    public ProcurementController(FormulaAiManagementService service) {
        this.service = service;
    }

    @PostMapping("/api/procurement/recommend")
    public ProcurementRecommendationResponse recommendProcurement(
            @Valid @RequestBody ProcurementRecommendationRequest request) {
        return service.recommendProcurement(request);
    }

    @GetMapping("/api/procurement/recommendations/{formulaId}")
    public ProcurementRecommendationResponse listProcurementRecommendations(@PathVariable String formulaId) {
        return service.listProcurementRecommendations(formulaId);
    }

    @PatchMapping("/api/procurement/recommendations/{formulaId}/{ingredientId}/status")
    public ProcurementStatusUpdateResponse updateProcurementStatus(
            @PathVariable String formulaId,
            @PathVariable String ingredientId,
            @RequestBody Map<String, String> request) {
        return service.updateProcurementStatus(formulaId, ingredientId, request.get("status"));
    }
}
