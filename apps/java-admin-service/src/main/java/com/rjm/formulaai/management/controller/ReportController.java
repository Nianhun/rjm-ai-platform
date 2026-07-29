package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ReportController {
    private final FormulaAiManagementService service;

    public ReportController(FormulaAiManagementService service) {
        this.service = service;
    }

    @PostMapping("/api/reports/feedback-impact")
    public FeedbackImpactReport buildFeedbackImpactReport(@Valid @RequestBody FormulaRequest request) {
        return service.buildFeedbackImpactReport(request);
    }
}
