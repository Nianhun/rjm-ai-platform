package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;
import javax.validation.constraints.NotBlank;

public class FormulaScreeningRequest {
    @NotBlank
    private String engineer;

    @NotBlank
    private String decision;

    @NotBlank
    private String reason;

    private List<FormulaIngredient> modifiedIngredients = new ArrayList<FormulaIngredient>();

    public FormulaScreeningRequest() {
    }

    public FormulaScreeningRequest(String engineer, String decision, String reason, List<FormulaIngredient> modifiedIngredients) {
        this.engineer = engineer;
        this.decision = decision;
        this.reason = reason;
        this.modifiedIngredients = modifiedIngredients;
    }

    public String getEngineer() {
        return engineer;
    }

    public void setEngineer(String engineer) {
        this.engineer = engineer;
    }

    public String getDecision() {
        return decision;
    }

    public void setDecision(String decision) {
        this.decision = decision;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public List<FormulaIngredient> getModifiedIngredients() {
        return modifiedIngredients;
    }

    public void setModifiedIngredients(List<FormulaIngredient> modifiedIngredients) {
        this.modifiedIngredients = modifiedIngredients;
    }
}
