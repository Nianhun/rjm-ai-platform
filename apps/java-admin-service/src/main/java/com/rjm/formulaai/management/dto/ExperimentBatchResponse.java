package com.rjm.formulaai.management.dto;

import java.util.List;
import java.util.Map;

public class ExperimentBatchResponse {
    private String batchNo;
    private String formulaId;
    private String stage;
    private String owner;
    private Map<String, Object> metrics;
    private List<String> issues;
    private String conclusion;
    private String status;
    private String createdAt;

    public ExperimentBatchResponse() {
    }

    public ExperimentBatchResponse(
            String batchNo,
            String formulaId,
            String stage,
            String owner,
            Map<String, Object> metrics,
            List<String> issues,
            String conclusion,
            String status,
            String createdAt) {
        this.batchNo = batchNo;
        this.formulaId = formulaId;
        this.stage = stage;
        this.owner = owner;
        this.metrics = metrics;
        this.issues = issues;
        this.conclusion = conclusion;
        this.status = status;
        this.createdAt = createdAt;
    }

    public String getBatchNo() {
        return batchNo;
    }

    public void setBatchNo(String batchNo) {
        this.batchNo = batchNo;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public String getStage() {
        return stage;
    }

    public void setStage(String stage) {
        this.stage = stage;
    }

    public String getOwner() {
        return owner;
    }

    public void setOwner(String owner) {
        this.owner = owner;
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

    public String getConclusion() {
        return conclusion;
    }

    public void setConclusion(String conclusion) {
        this.conclusion = conclusion;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}
