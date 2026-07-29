package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class FormulaLearningExplanationResponse {
    private String formulaId;
    private String goal;
    private List<LearnedWeightRow> influences = new ArrayList<LearnedWeightRow>();

    public FormulaLearningExplanationResponse() {
    }

    public FormulaLearningExplanationResponse(String formulaId, String goal, List<LearnedWeightRow> influences) {
        this.formulaId = formulaId;
        this.goal = goal;
        this.influences = influences;
    }

    public String getFormulaId() {
        return formulaId;
    }

    public void setFormulaId(String formulaId) {
        this.formulaId = formulaId;
    }

    public String getGoal() {
        return goal;
    }

    public void setGoal(String goal) {
        this.goal = goal;
    }

    public List<LearnedWeightRow> getInfluences() {
        return influences;
    }

    public void setInfluences(List<LearnedWeightRow> influences) {
        this.influences = influences;
    }
}
