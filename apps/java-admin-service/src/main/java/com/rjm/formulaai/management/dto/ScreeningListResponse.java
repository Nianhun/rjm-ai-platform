package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class ScreeningListResponse {
    private String formulaId;
    private List<ScreeningRecord> records = new ArrayList<ScreeningRecord>();

    public ScreeningListResponse() {
    }

    public ScreeningListResponse(String formulaId, List<ScreeningRecord> records) {
        this.formulaId = formulaId;
        this.records = records;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public List<ScreeningRecord> getRecords() {
        return records;
    }

    public void setRecords(List<ScreeningRecord> records) {
        this.records = records;
    }
}
