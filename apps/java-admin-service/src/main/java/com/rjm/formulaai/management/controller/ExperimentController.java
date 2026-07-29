package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.ExperimentBatchListResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchRequest;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;
import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ExperimentController {
    private final FormulaAiManagementService service;

    public ExperimentController(FormulaAiManagementService service) {
        this.service = service;
    }

    @PostMapping("/api/experiments/feedback")
    public FeedbackStoredResponse recordExperimentFeedback(@Valid @RequestBody ExperimentFeedbackRequest request) {
        return service.recordExperimentFeedback(request);
    }

    @PostMapping("/api/experiments/batches")
    public ExperimentBatchResponse createExperimentBatch(@Valid @RequestBody ExperimentBatchRequest request) {
        return service.createExperimentBatch(request);
    }

    @GetMapping("/api/experiments/batches")
    public ExperimentBatchListResponse listExperimentBatches(@RequestParam("formula_id") String formulaId) {
        return service.listExperimentBatches(formulaId);
    }
}
