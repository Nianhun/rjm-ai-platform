package com.rjm.formulaai.management.dto;

import java.util.List;

public class ExperimentBatchListResponse {
    private String formulaId;
    private List<ExperimentBatchResponse> batches;

    public ExperimentBatchListResponse() {
    }

    public ExperimentBatchListResponse(String formulaId, List<ExperimentBatchResponse> batches) {
        this.formulaId = formulaId;
        this.batches = batches;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public List<ExperimentBatchResponse> getBatches() {
        return batches;
    }

    public void setBatches(List<ExperimentBatchResponse> batches) {
        this.batches = batches;
    }
}
