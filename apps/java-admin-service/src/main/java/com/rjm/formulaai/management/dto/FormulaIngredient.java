package com.rjm.formulaai.management.dto;

import java.math.BigDecimal;

public class FormulaIngredient {
    private String ingredientId;
    private String role;
    private BigDecimal suggestedPercentMin;
    private BigDecimal suggestedPercentMax;

    public FormulaIngredient() {
    }

    public FormulaIngredient(String ingredientId, String role, BigDecimal suggestedPercentMin, BigDecimal suggestedPercentMax) {
        this.ingredientId = ingredientId;
        this.role = role;
        this.suggestedPercentMin = suggestedPercentMin;
        this.suggestedPercentMax = suggestedPercentMax;
    }

    public String getIngredientId() {
        return ingredientId;
    }

    public void setIngredientId(String ingredientId) {
        this.ingredientId = ingredientId;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public BigDecimal getSuggestedPercentMin() {
        return suggestedPercentMin;
    }

    public void setSuggestedPercentMin(BigDecimal suggestedPercentMin) {
        this.suggestedPercentMin = suggestedPercentMin;
    }

    public BigDecimal getSuggestedPercentMax() {
        return suggestedPercentMax;
    }

    public void setSuggestedPercentMax(BigDecimal suggestedPercentMax) {
        this.suggestedPercentMax = suggestedPercentMax;
    }
}
