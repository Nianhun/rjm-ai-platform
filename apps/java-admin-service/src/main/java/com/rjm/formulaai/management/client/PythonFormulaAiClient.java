package com.rjm.formulaai.management.client;

import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import java.net.URI;
import java.util.Map;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

public class PythonFormulaAiClient {
    private final RestTemplate restTemplate;
    private final String baseUrl;

    public PythonFormulaAiClient(RestTemplate restTemplate, String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = trimTrailingSlash(baseUrl);
    }

    public FormulaRecommendationResponse recommendFormulas(FormulaRequest request) {
        return restTemplate.postForObject(baseUrl + "/recommend", request, FormulaRecommendationResponse.class);
    }

    public AiChatResponse chat(AiChatRequest request) {
        return restTemplate.postForObject(baseUrl + "/chat", request, AiChatResponse.class);
    }

    public FeedbackStoredResponse recordExperimentFeedback(ExperimentFeedbackRequest request) {
        return restTemplate.postForObject(baseUrl + "/feedback", request, FeedbackStoredResponse.class);
    }

    public ProcurementRecommendationResponse recommendProcurement(ProcurementRecommendationRequest request) {
        return restTemplate.postForObject(
                baseUrl + "/procurement/recommend",
                request,
                ProcurementRecommendationResponse.class);
    }

    public FeedbackImpactReport buildFeedbackImpactReport(FormulaRequest request) {
        return restTemplate.postForObject(
                baseUrl + "/reports/feedback-impact",
                request,
                FeedbackImpactReport.class);
    }

    public ScreeningStoredResponse recordFormulaScreening(String formulaId, FormulaScreeningRequest request) {
        PythonScreeningRequest payload = new PythonScreeningRequest(formulaId, request);
        return restTemplate.postForObject(baseUrl + "/screening", payload, ScreeningStoredResponse.class);
    }

    public ScreeningListResponse listFormulaScreenings(String formulaId) {
        String url = UriComponentsBuilder.fromHttpUrl(baseUrl + "/screening")
                .queryParam("formula_id", formulaId)
                .toUriString();
        return restTemplate.getForObject(url, ScreeningListResponse.class);
    }

    public KnowledgeStatusResponse getKnowledgeStatus() {
        return restTemplate.getForObject(baseUrl + "/knowledge/status", KnowledgeStatusResponse.class);
    }

    public Map getYuxiEntityNames() {
        return restTemplate.getForObject(baseUrl + "/knowledge/entity-names", Map.class);
    }

    public KnowledgeGovernanceResponse getKnowledgeGovernance() {
        return restTemplate.getForObject(baseUrl + "/knowledge/governance", KnowledgeGovernanceResponse.class);
    }

    public Map getElementGraph(String elementId) {
        URI uri = UriComponentsBuilder.fromHttpUrl(baseUrl)
                .pathSegment("knowledge", "elements", elementId, "graph")
                .build()
                .encode()
                .toUri();
        return restTemplate.getForObject(uri, Map.class);
    }

    public EvidenceResponse getEvidence(String evidenceId) {
        return restTemplate.getForObject(baseUrl + "/evidence/" + evidenceId, EvidenceResponse.class);
    }

    public Map getArchivedFormula(String formulaId) {
        return restTemplate.getForObject(baseUrl + "/formulas/" + formulaId, Map.class);
    }

    private String trimTrailingSlash(String value) {
        if (value == null || value.length() == 0) {
            return "";
        }
        return value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
    }

    private static class PythonScreeningRequest {
        private String formulaId;
        private String engineer;
        private String decision;
        private String reason;
        private java.util.List<com.rjm.formulaai.management.dto.FormulaIngredient> modifiedIngredients;

        PythonScreeningRequest(String formulaId, FormulaScreeningRequest request) {
            this.formulaId = formulaId;
            this.engineer = request.getEngineer();
            this.decision = request.getDecision();
            this.reason = request.getReason();
            this.modifiedIngredients = request.getModifiedIngredients();
        }

        public String getFormulaId() {
            return formulaId;
        }

        public String getEngineer() {
            return engineer;
        }

        public String getDecision() {
            return decision;
        }

        public String getReason() {
            return reason;
        }

        public java.util.List<com.rjm.formulaai.management.dto.FormulaIngredient> getModifiedIngredients() {
            return modifiedIngredients;
        }
    }
}
