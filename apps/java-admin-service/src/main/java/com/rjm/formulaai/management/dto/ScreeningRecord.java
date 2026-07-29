package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class ScreeningRecord {
    private String formulaId;
    private String engineer;
    private String decision;
    private String reason;
    private List<FormulaIngredient> modifiedIngredients = new ArrayList<FormulaIngredient>();

    public ScreeningRecord() {
    }

    public ScreeningRecord(String formulaId, String engineer, String decision, String reason,
            List<FormulaIngredient> modifiedIngredients) {
        this.formulaId = formulaId;
        this.engineer = engineer;
        this.decision = decision;
        this.reason = reason;
        this.modifiedIngredients = modifiedIngredients;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
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
