package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FormulaController {
    private final FormulaAiManagementService service;

    public FormulaController(FormulaAiManagementService service) {
        this.service = service;
    }

    @PostMapping("/api/formulas/recommend")
    public FormulaRecommendationResponse recommendFormulas(@Valid @RequestBody FormulaRequest request) {
        return service.recommendFormulas(request);
    }

    @PostMapping("/api/formulas/{formulaId}/screenings")
    public ScreeningStoredResponse recordFormulaScreening(
            @PathVariable String formulaId,
            @Valid @RequestBody FormulaScreeningRequest request) {
        return service.recordFormulaScreening(formulaId, request);
    }

    @GetMapping("/api/formulas/{formulaId}/screenings")
    public ScreeningListResponse listFormulaScreenings(@PathVariable String formulaId) {
        return service.listFormulaScreenings(formulaId);
    }
}
