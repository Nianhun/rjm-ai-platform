package com.rjm.formulaai.management.dto;

import java.util.List;
import java.util.Map;

public class KnowledgeGovernanceResponse extends KnowledgeStatusResponse {
    private Map<String, Integer> evidenceSourceTypeCounts;
    private Map<String, Integer> relationTypeCounts;
    private Map<String, Integer> relationConfidenceCounts;
    private int ingredientAliasCount;
    private List<String> missingEvidenceIds;
    private int warningCount;
    private List<String> warnings;
    private List<String> governanceNotes;

    public KnowledgeGovernanceResponse() {
    }

    public KnowledgeGovernanceResponse(
            int ingredientCount,
            int relationCount,
            int rawMaterialSkuCount,
            int evidenceCount,
            Map<String, String> sourcePaths,
            Map<String, Integer> evidencePrefixCounts,
            Map<String, Integer> evidenceSourceTypeCounts,
            Map<String, Integer> relationTypeCounts,
            Map<String, Integer> relationConfidenceCounts,
            int ingredientAliasCount,
            List<String> missingEvidenceIds,
            int warningCount,
            List<String> warnings,
            List<String> governanceNotes) {
        super(ingredientCount, relationCount, rawMaterialSkuCount, evidenceCount, sourcePaths, evidencePrefixCounts);
        this.evidenceSourceTypeCounts = evidenceSourceTypeCounts;
        this.relationTypeCounts = relationTypeCounts;
        this.relationConfidenceCounts = relationConfidenceCounts;
        this.ingredientAliasCount = ingredientAliasCount;
        this.missingEvidenceIds = missingEvidenceIds;
        this.warningCount = warningCount;
        this.warnings = warnings;
        this.governanceNotes = governanceNotes;
    }

    public Map<String, Integer> getEvidenceSourceTypeCounts() {
        return evidenceSourceTypeCounts;
    }

    public void setEvidenceSourceTypeCounts(Map<String, Integer> evidenceSourceTypeCounts) {
        this.evidenceSourceTypeCounts = evidenceSourceTypeCounts;
    }

    public Map<String, Integer> getRelationTypeCounts() {
        return relationTypeCounts;
    }

    public void setRelationTypeCounts(Map<String, Integer> relationTypeCounts) {
        this.relationTypeCounts = relationTypeCounts;
    }

    public Map<String, Integer> getRelationConfidenceCounts() {
        return relationConfidenceCounts;
    }

    public void setRelationConfidenceCounts(Map<String, Integer> relationConfidenceCounts) {
        this.relationConfidenceCounts = relationConfidenceCounts;
    }

    public int getIngredientAliasCount() {
        return ingredientAliasCount;
    }

    public void setIngredientAliasCount(int ingredientAliasCount) {
        this.ingredientAliasCount = ingredientAliasCount;
    }

    public List<String> getMissingEvidenceIds() {
        return missingEvidenceIds;
    }

    public void setMissingEvidenceIds(List<String> missingEvidenceIds) {
        this.missingEvidenceIds = missingEvidenceIds;
    }

    public int getWarningCount() {
        return warningCount;
    }

    public void setWarningCount(int warningCount) {
        this.warningCount = warningCount;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public List<String> getGovernanceNotes() {
        return governanceNotes;
    }

    public void setGovernanceNotes(List<String> governanceNotes) {
        this.governanceNotes = governanceNotes;
    }
}
