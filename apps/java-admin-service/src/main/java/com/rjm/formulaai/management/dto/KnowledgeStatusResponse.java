package com.rjm.formulaai.management.dto;

import java.util.Map;

public class KnowledgeStatusResponse {
    private int ingredientCount;
    private int relationCount;
    private int rawMaterialSkuCount;
    private int evidenceCount;
    private String knowledgeSource;
    private Map<String, Object> yuxiGraph;
    private Map<String, String> sourcePaths;
    private Map<String, Integer> evidencePrefixCounts;

    public KnowledgeStatusResponse() {
    }

    public KnowledgeStatusResponse(
            int ingredientCount,
            int relationCount,
            int rawMaterialSkuCount,
            int evidenceCount,
            Map<String, String> sourcePaths,
            Map<String, Integer> evidencePrefixCounts) {
        this.ingredientCount = ingredientCount;
        this.relationCount = relationCount;
        this.rawMaterialSkuCount = rawMaterialSkuCount;
        this.evidenceCount = evidenceCount;
        this.sourcePaths = sourcePaths;
        this.evidencePrefixCounts = evidencePrefixCounts;
    }

    public int getIngredientCount() {
        return ingredientCount;
    }

    public void setIngredientCount(int ingredientCount) {
        this.ingredientCount = ingredientCount;
    }

    public int getRelationCount() {
        return relationCount;
    }

    public void setRelationCount(int relationCount) {
        this.relationCount = relationCount;
    }

    public int getRawMaterialSkuCount() {
        return rawMaterialSkuCount;
    }

    public void setRawMaterialSkuCount(int rawMaterialSkuCount) {
        this.rawMaterialSkuCount = rawMaterialSkuCount;
    }

    public int getEvidenceCount() {
        return evidenceCount;
    }

    public void setEvidenceCount(int evidenceCount) {
        this.evidenceCount = evidenceCount;
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

    public Map<String, String> getSourcePaths() {
        return sourcePaths;
    }

    public void setSourcePaths(Map<String, String> sourcePaths) {
        this.sourcePaths = sourcePaths;
    }

    public Map<String, Integer> getEvidencePrefixCounts() {
        return evidencePrefixCounts;
    }

    public void setEvidencePrefixCounts(Map<String, Integer> evidencePrefixCounts) {
        this.evidencePrefixCounts = evidencePrefixCounts;
    }
}
