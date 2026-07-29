package com.rjm.formulaai.management.dto;

public class ScreeningStoredResponse {
    private boolean stored;
    private int screeningCount;

    public ScreeningStoredResponse() {
    }

    public ScreeningStoredResponse(boolean stored, int screeningCount) {
        this.stored = stored;
        this.screeningCount = screeningCount;
    }

    public boolean isStored() {
        return stored;
    }

    public void setStored(boolean stored) {
        this.stored = stored;
    }

    public int getScreeningCount() {
        return screeningCount;
    }

    public void setScreeningCount(int screeningCount) {
        this.screeningCount = screeningCount;
    }
}
