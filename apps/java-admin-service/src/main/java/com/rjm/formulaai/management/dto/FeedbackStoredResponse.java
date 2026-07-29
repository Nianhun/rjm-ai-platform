package com.rjm.formulaai.management.dto;

public class FeedbackStoredResponse {
    private boolean stored;
    private int feedbackCount;

    public FeedbackStoredResponse() {
    }

    public FeedbackStoredResponse(boolean stored, int feedbackCount) {
        this.stored = stored;
        this.feedbackCount = feedbackCount;
    }

    public boolean isStored() {
        return stored;
    }

    public void setStored(boolean stored) {
        this.stored = stored;
    }

    public int getFeedbackCount() {
        return feedbackCount;
    }

    public void setFeedbackCount(int feedbackCount) {
        this.feedbackCount = feedbackCount;
    }
}
