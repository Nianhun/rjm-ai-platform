package com.rjm.formulaai.management.dto;

import java.util.ArrayList;
import java.util.List;

public class FeedbackImpactReport {
    private String requestId;
    private String goal;
    private int feedbackCount;
    private List<FeedbackImpactRow> rows = new ArrayList<FeedbackImpactRow>();

    public FeedbackImpactReport() {
    }

    public FeedbackImpactReport(String requestId, String goal, int feedbackCount, List<FeedbackImpactRow> rows) {
        this.requestId = requestId;
        this.goal = goal;
        this.feedbackCount = feedbackCount;
        this.rows = rows;
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

    public int getFeedbackCount() {
        return feedbackCount;
    }

    public void setFeedbackCount(int feedbackCount) {
        this.feedbackCount = feedbackCount;
    }

    public List<FeedbackImpactRow> getRows() {
        return rows;
    }

    public void setRows(List<FeedbackImpactRow> rows) {
        this.rows = rows;
    }
}
