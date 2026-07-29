package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;

public class ExperimentFeedbackRequest {
    @NotBlank
    private String formulaId;

    @NotBlank
    private String batchNo;

    @NotBlank
    private String result;

    @NotEmpty
    private List<String> ingredientIds = new ArrayList<String>();

    private Map<String, Object> metrics = new LinkedHashMap<String, Object>();
    private List<String> issues = new ArrayList<String>();
    private String engineerConclusion;
    private String engineer;
    private String createdAt;

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public String getBatchNo() {
        return batchNo;
    }

    public void setBatchNo(String batchNo) {
        this.batchNo = batchNo;
    }

    public String getResult() {
        return result;
    }

    public void setResult(String result) {
        this.result = result;
    }

    public List<String> getIngredientIds() {
        return ingredientIds;
    }

    public void setIngredientIds(List<String> ingredientIds) {
        this.ingredientIds = ingredientIds;
    }

    public Map<String, Object> getMetrics() {
        return metrics;
    }

    public void setMetrics(Map<String, Object> metrics) {
        this.metrics = metrics;
    }

    public List<String> getIssues() {
        return issues;
    }

    public void setIssues(List<String> issues) {
        this.issues = issues;
    }

    public String getEngineerConclusion() {
        return engineerConclusion;
    }

    public void setEngineerConclusion(String engineerConclusion) {
        this.engineerConclusion = engineerConclusion;
    }

    public String getEngineer() {
        return engineer;
    }

    public void setEngineer(String engineer) {
        this.engineer = engineer;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}
