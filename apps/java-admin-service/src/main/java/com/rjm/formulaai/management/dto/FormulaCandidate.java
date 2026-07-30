package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class FormulaCandidate {
    private String id;
    private String requestId;
    private String goal;
    private String strategy;
    private List<FormulaIngredient> ingredients = new ArrayList<FormulaIngredient>();
    private String recommendationReason;
    private List<String> riskNotes = new ArrayList<String>();
    private List<String> evidenceIds = new ArrayList<String>();
    private FormulaScore score;
    private String status;

    public FormulaCandidate() {
    }

    public FormulaCandidate(String id, String requestId, String goal, List<FormulaIngredient> ingredients,
            String recommendationReason, List<String> riskNotes, List<String> evidenceIds, FormulaScore score,
            String status) {
        this.id = id;
        this.requestId = requestId;
        this.goal = goal;
        this.strategy = "knowledge_graph_ai";
        this.ingredients = ingredients;
        this.recommendationReason = recommendationReason;
        this.riskNotes = riskNotes;
        this.evidenceIds = evidenceIds;
        this.score = score;
        this.status = status;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public String getGoal() {
        return goal;
    }

    public void setGoal(String goal) {
        this.goal = goal;
    }

    public String getStrategy() {
        return strategy;
    }

    public void setStrategy(String strategy) {
        this.strategy = strategy;
    }

    public List<FormulaIngredient> getIngredients() {
        return ingredients;
    }

    public void setIngredients(List<FormulaIngredient> ingredients) {
        this.ingredients = ingredients;
    }

    public String getRecommendationReason() {
        return recommendationReason;
    }

    public void setRecommendationReason(String recommendationReason) {
        this.recommendationReason = recommendationReason;
    }

    public List<String> getRiskNotes() {
        return riskNotes;
    }

    public void setRiskNotes(List<String> riskNotes) {
        this.riskNotes = riskNotes;
    }

    public List<String> getEvidenceIds() {
        return evidenceIds;
    }

    public void setEvidenceIds(List<String> evidenceIds) {
        this.evidenceIds = evidenceIds;
    }

    public FormulaScore getScore() {
        return score;
    }

    public void setScore(FormulaScore score) {
        this.score = score;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
