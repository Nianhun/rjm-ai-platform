package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.service.FormulaAiManagementService;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class FormulaArchiveController {
    private final FormulaAiManagementService service;

    public FormulaArchiveController(FormulaAiManagementService service) {
        this.service = service;
    }

    @GetMapping("/api/formulas/{formulaId}")
    public ResponseEntity<Map> getArchivedFormula(@PathVariable String formulaId) {
        Map archived = service.getArchivedFormula(formulaId);
        if (archived == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(archived);
    }
}
