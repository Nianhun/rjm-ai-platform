package com.rjm.formulaai.management.persistence;

public class ProcurementStatusUpdateResponse {
    private boolean updated;
    private String formulaId;
    private String ingredientId;
    private String status;

    public ProcurementStatusUpdateResponse() {
    }

    public ProcurementStatusUpdateResponse(boolean updated, String formulaId, String ingredientId, String status) {
        this.updated = updated;
        this.formulaId = formulaId;
        this.ingredientId = ingredientId;
        this.status = status;
    }

    public boolean isUpdated() {
        return updated;
    }

    public void setUpdated(boolean updated) {
        this.updated = updated;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public String getIngredientId() {
        return ingredientId;
    }

    public void setIngredientId(String ingredientId) {
        this.ingredientId = ingredientId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
