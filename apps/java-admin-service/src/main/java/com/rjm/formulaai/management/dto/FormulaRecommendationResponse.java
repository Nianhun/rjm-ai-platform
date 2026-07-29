package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class FormulaRecommendationResponse {
    private String requestId;
    private String goal;
    private String strategy;
    private String knowledgeSource;
    private Map<String, Object> yuxiGraph;
    private List<FormulaCandidate> formulas = new ArrayList<FormulaCandidate>();

    public FormulaRecommendationResponse() {
    }

    public FormulaRecommendationResponse(String requestId, String goal, List<FormulaCandidate> formulas) {
        this.requestId = requestId;
        this.goal = goal;
        this.strategy = "baseline";
        this.formulas = formulas;
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

    public String getKnowledgeSource() {
        return knowledgeSource;
    }

    public void setKnowledgeSource(String knowledgeSource) {
        this.knowledgeSource = knowledgeSource;
    }

    public Map<String, Object> getYuxiGraph() {
        return yuxiGraph;
    }

    public void setYuxiGraph(Map<String, Object> yuxiGraph) {
        this.yuxiGraph = yuxiGraph;
    }

    public List<FormulaCandidate> getFormulas() {
        return formulas;
    }

    public void setFormulas(List<FormulaCandidate> formulas) {
        this.formulas = formulas;
    }
}
