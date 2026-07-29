package com.rjm.formulaai.management.dto;

import java.math.BigDecimal;

public class FormulaScore {
    private BigDecimal efficacy;
    private BigDecimal stability;
    private BigDecimal skinFeel;
    private BigDecimal cost;
    private BigDecimal supply;
    private BigDecimal overall;

    public FormulaScore() {
    }

    public FormulaScore(BigDecimal efficacy, BigDecimal stability, BigDecimal skinFeel, BigDecimal cost,
            BigDecimal supply, BigDecimal overall) {
        this.efficacy = efficacy;
        this.stability = stability;
        this.skinFeel = skinFeel;
        this.cost = cost;
        this.supply = supply;
        this.overall = overall;
    }

    public BigDecimal getEfficacy() {
        return efficacy;
    }

    public void setEfficacy(BigDecimal efficacy) {
        this.efficacy = efficacy;
    }

    public BigDecimal getStability() {
        return stability;
    }

    public void setStability(BigDecimal stability) {
        this.stability = stability;
    }

    public BigDecimal getSkinFeel() {
        return skinFeel;
    }

    public void setSkinFeel(BigDecimal skinFeel) {
        this.skinFeel = skinFeel;
    }

    public BigDecimal getCost() {
        return cost;
    }

    public void setCost(BigDecimal cost) {
        this.cost = cost;
    }

    public BigDecimal getSupply() {
        return supply;
    }

    public void setSupply(BigDecimal supply) {
        this.supply = supply;
    }

    public BigDecimal getOverall() {
        return overall;
    }

    public void setOverall(BigDecimal overall) {
        this.overall = overall;
    }
}
