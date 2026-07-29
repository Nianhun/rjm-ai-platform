package com.rjm.formulaai.management.dto;

import java.math.BigDecimal;

public class LearnedWeightRow {
    private String goal;
    private String targetType;
    private String targetKey;
    private BigDecimal weight;
    private int evidenceCount;
    private String source;
    private String calculationNote;

    public LearnedWeightRow() {
    }

    public LearnedWeightRow(String goal, String targetType, String targetKey, BigDecimal weight,
            int evidenceCount, String source, String calculationNote) {
        this.goal = goal;
        this.targetType = targetType;
        this.targetKey = targetKey;
        this.weight = weight;
        this.evidenceCount = evidenceCount;
        this.source = source;
        this.calculationNote = calculationNote;
    }

    public String getGoal() {
        return goal;
    }

    public void setGoal(String goal) {
        this.goal = goal;
    }

    public String getTargetType() {
        return targetType;
    }

    public void setTargetType(String targetType) {
        this.targetType = targetType;
    }

    public String getTargetKey() {
        return targetKey;
    }

    public void setTargetKey(String targetKey) {
        this.targetKey = targetKey;
    }

    public BigDecimal getWeight() {
        return weight;
    }

    public void setWeight(BigDecimal weight) {
        this.weight = weight;
    }

    public int getEvidenceCount() {
        return evidenceCount;
    }

    public void setEvidenceCount(int evidenceCount) {
        this.evidenceCount = evidenceCount;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getCalculationNote() {
        return calculationNote;
    }

    public void setCalculationNote(String calculationNote) {
        this.calculationNote = calculationNote;
    }
}
