package com.rjm.formulaai.management.dto;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class FeedbackImpactRow {
    private String formulaId;
    private Integer baselineRank;
    private Integer learnedRank;
    private BigDecimal baselineScore;
    private BigDecimal learnedScore;
    private BigDecimal scoreDelta;
    private List<String> ingredientIds = new ArrayList<String>();

    public FeedbackImpactRow() {
    }

    public FeedbackImpactRow(String formulaId, Integer baselineRank, Integer learnedRank, BigDecimal baselineScore,
            BigDecimal learnedScore, BigDecimal scoreDelta, List<String> ingredientIds) {
        this.formulaId = formulaId;
        this.baselineRank = baselineRank;
        this.learnedRank = learnedRank;
        this.baselineScore = baselineScore;
        this.learnedScore = learnedScore;
        this.scoreDelta = scoreDelta;
        this.ingredientIds = ingredientIds;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public Integer getBaselineRank() {
        return baselineRank;
    }

    public void setBaselineRank(Integer baselineRank) {
        this.baselineRank = baselineRank;
    }

    public Integer getLearnedRank() {
        return learnedRank;
    }

    public void setLearnedRank(Integer learnedRank) {
        this.learnedRank = learnedRank;
    }

    public BigDecimal getBaselineScore() {
        return baselineScore;
    }

    public void setBaselineScore(BigDecimal baselineScore) {
        this.baselineScore = baselineScore;
    }

    public BigDecimal getLearnedScore() {
        return learnedScore;
    }

    public void setLearnedScore(BigDecimal learnedScore) {
        this.learnedScore = learnedScore;
    }

    public BigDecimal getScoreDelta() {
        return scoreDelta;
    }

    public void setScoreDelta(BigDecimal scoreDelta) {
        this.scoreDelta = scoreDelta;
    }

    public List<String> getIngredientIds() {
        return ingredientIds;
    }

    public void setIngredientIds(List<String> ingredientIds) {
        this.ingredientIds = ingredientIds;
    }
}
