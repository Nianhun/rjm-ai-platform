package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class AiChatResponse {
    private String messageId;
    private String knowledgeSource;
    private Map<String, Object> yuxiGraph = new LinkedHashMap<String, Object>();
    private String answer;
    private List<String> followUpQuestions = new ArrayList<String>();
    private List<String> ingredientIds = new ArrayList<String>();
    private List<String> evidenceIds = new ArrayList<String>();

    public String getMessageId() {
        return messageId;
    }

    public void setMessageId(String messageId) {
        this.messageId = messageId;
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

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<String> getFollowUpQuestions() {
        return followUpQuestions;
    }

    public void setFollowUpQuestions(List<String> followUpQuestions) {
        this.followUpQuestions = followUpQuestions;
    }

    public List<String> getIngredientIds() {
        return ingredientIds;
    }

    public void setIngredientIds(List<String> ingredientIds) {
        this.ingredientIds = ingredientIds;
    }

    public List<String> getEvidenceIds() {
        return evidenceIds;
    }

    public void setEvidenceIds(List<String> evidenceIds) {
        this.evidenceIds = evidenceIds;
    }
}
