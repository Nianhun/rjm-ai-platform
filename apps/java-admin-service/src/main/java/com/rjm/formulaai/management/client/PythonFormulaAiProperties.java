package com.rjm.formulaai.management.client;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "rjm.python-ai")
public class PythonFormulaAiProperties {
    private String baseUrl = "http://127.0.0.1:8000";

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }
}
