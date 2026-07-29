package com.rjm.formulaai.management.persistence;

import java.math.BigDecimal;

public class LearnedWeightRecord {
    private final String goal;
    private final String targetType;
    private final String targetKey;
    private final BigDecimal weight;
    private final int evidenceCount;
    private final String source;
    private final String calculationNote;

    public LearnedWeightRecord(String goal, String targetType, String targetKey, BigDecimal weight,
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

    public String getTargetType() {
        return targetType;
    }

    public String getTargetKey() {
        return targetKey;
    }

    public BigDecimal getWeight() {
        return weight;
    }

    public int getEvidenceCount() {
        return evidenceCount;
    }

    public String getSource() {
        return source;
    }

    public String getCalculationNote() {
        return calculationNote;
    }
}
