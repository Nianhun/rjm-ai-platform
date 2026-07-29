package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class ProcurementRecommendationResponse {
    private String formulaId;
    private List<ProcurementItem> items = new ArrayList<ProcurementItem>();

    public ProcurementRecommendationResponse() {
    }

    public ProcurementRecommendationResponse(String formulaId, List<ProcurementItem> items) {
        this.formulaId = formulaId;
        this.items = items;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public List<ProcurementItem> getItems() {
        return items;
    }

    public void setItems(List<ProcurementItem> items) {
        this.items = items;
    }
}
