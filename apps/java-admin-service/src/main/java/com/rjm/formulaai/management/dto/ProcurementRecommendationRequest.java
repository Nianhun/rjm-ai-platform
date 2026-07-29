package com.rjm.formulaai.management.dto;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;

public class ProcurementRecommendationRequest {
    @Valid
    @NotNull
    private FormulaCandidate formula;

    public ProcurementRecommendationRequest() {
    }

    public ProcurementRecommendationRequest(FormulaCandidate formula) {
        this.formula = formula;
    }

    public FormulaCandidate getFormula() {
        return formula;
    }

    public void setFormula(FormulaCandidate formula) {
        this.formula = formula;
    }
}
