package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class LearnedWeightResponse {
    private String goal;
    private String targetType;
    private List<LearnedWeightRow> weights = new ArrayList<LearnedWeightRow>();

    public LearnedWeightResponse() {
    }

    public LearnedWeightResponse(String goal, String targetType, List<LearnedWeightRow> weights) {
        this.goal = goal;
        this.targetType = targetType;
        this.weights = weights;
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

    public List<LearnedWeightRow> getWeights() {
        return weights;
    }

    public void setWeights(List<LearnedWeightRow> weights) {
        this.weights = weights;
    }
}
