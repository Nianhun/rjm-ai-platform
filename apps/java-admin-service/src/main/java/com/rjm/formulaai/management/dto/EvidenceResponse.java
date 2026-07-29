package com.rjm.formulaai.management.dto;

import java.util.Map;

public class EvidenceResponse {
    private String id;
    private String sourceType;
    private String title;
    private String summary;
    private String sourceUrl;
    private Map<String, Object> metadata;

    public EvidenceResponse() {
    }

    public EvidenceResponse(String id, String sourceType, String title, String summary, String sourceUrl, Map<String, Object> metadata) {
        this.id = id;
        this.sourceType = sourceType;
        this.title = title;
        this.summary = summary;
        this.sourceUrl = sourceUrl;
        this.metadata = metadata;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getSourceType() {
        return sourceType;
    }

    public void setSourceType(String sourceType) {
        this.sourceType = sourceType;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public String getSourceUrl() {
        return sourceUrl;
    }

    public void setSourceUrl(String sourceUrl) {
        this.sourceUrl = sourceUrl;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }
}
