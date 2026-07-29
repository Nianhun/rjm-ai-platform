package com.rjm.formulaai.management.dto;

import java.util.LinkedHashMap;
import java.util.Map;
import javax.validation.constraints.NotBlank;

public class FormulaRequest {
    @NotBlank
    private String id;

    @NotBlank
    private String goal;

    private String dosageForm;

    private Map<String, Object> constraints = new LinkedHashMap<String, Object>();

    public FormulaRequest() {
    }

    public FormulaRequest(String id, String goal, String dosageForm, Map<String, Object> constraints) {
        this.id = id;
        this.goal = goal;
        this.dosageForm = dosageForm;
        this.constraints = constraints;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getGoal() {
        return goal;
    }

    public void setGoal(String goal) {
        this.goal = goal;
    }

    public String getDosageForm() {
        return dosageForm;
    }

    public void setDosageForm(String dosageForm) {
        this.dosageForm = dosageForm;
    }

    public Map<String, Object> getConstraints() {
        return constraints;
    }

    public void setConstraints(Map<String, Object> constraints) {
        this.constraints = constraints;
    }
}
