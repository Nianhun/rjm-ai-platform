package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class EvidenceController {
    private final FormulaAiManagementService service;

    public EvidenceController(FormulaAiManagementService service) {
        this.service = service;
    }

    @GetMapping("/api/evidence/{evidenceId}")
    public ResponseEntity<EvidenceResponse> getEvidence(@PathVariable String evidenceId) {
        EvidenceResponse evidence = service.getEvidence(evidenceId);
        if (evidence == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(evidence);
    }
}
