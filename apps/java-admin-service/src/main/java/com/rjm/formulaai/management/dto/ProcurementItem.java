package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class ProcurementItem {
    private String ingredientId;
    private String status;
    private List<RawMaterialSkuRecommendation> recommendedSkus = new ArrayList<RawMaterialSkuRecommendation>();

    public ProcurementItem() {
    }

    public ProcurementItem(String ingredientId, String status, List<RawMaterialSkuRecommendation> recommendedSkus) {
        this.ingredientId = ingredientId;
        this.status = status;
        this.recommendedSkus = recommendedSkus;
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

    public List<RawMaterialSkuRecommendation> getRecommendedSkus() {
        return recommendedSkus;
    }

    public void setRecommendedSkus(List<RawMaterialSkuRecommendation> recommendedSkus) {
        this.recommendedSkus = recommendedSkus;
    }
}
