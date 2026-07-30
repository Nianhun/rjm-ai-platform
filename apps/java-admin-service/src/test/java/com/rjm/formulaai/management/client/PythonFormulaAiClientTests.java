package com.rjm.formulaai.management.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaCandidate;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaScore;
import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import java.math.BigDecimal;
import java.util.Arrays;
import java.util.Collections;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;

class PythonFormulaAiClientTests {
    @Test
    void chatPostsMessageToPythonChatEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");
        AiChatRequest request = new AiChatRequest();
        request.setId("CHAT-JAVA-CLIENT");
        request.setMessage("保湿乳液如何降低粘腻感？");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/chat"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"id\":\"CHAT-JAVA-CLIENT\",\"message\":\"保湿乳液如何降低粘腻感？\",\"history\":[],\"context\":{}}"))
                .andRespond(withSuccess("{\"message_id\":\"CHAT-JAVA-CLIENT\",\"knowledge_source\":\"yuxi_graph_online\",\"answer\":\"优先调整油相和增稠体系。\",\"ingredient_ids\":[\"YUXI-ING\"],\"evidence_ids\":[\"YUXI-GRAPH-ING\"]}", MediaType.APPLICATION_JSON));

        AiChatResponse response = client.chat(request);

        assertEquals("CHAT-JAVA-CLIENT", response.getMessageId());
        assertEquals("yuxi_graph_online", response.getKnowledgeSource());
        assertEquals("优先调整油相和增稠体系。", response.getAnswer());
        fixture.server.verify();
    }

    @Test
    void recommendPostsSnakeCaseRequestToPythonService() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
        RestTemplate restTemplate = new RestTemplate(Collections.singletonList(new MappingJackson2HttpMessageConverter(objectMapper)));
        MockRestServiceServer server = MockRestServiceServer.bindTo(restTemplate).build();
        PythonFormulaAiClient client = new PythonFormulaAiClient(restTemplate, "http://127.0.0.1:8000");

        server.expect(requestTo("http://127.0.0.1:8000/recommend"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"id\":\"REQ-JAVA-CLIENT\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andRespond(withSuccess("{\"request_id\":\"REQ-JAVA-CLIENT\",\"goal\":\"保湿\",\"strategy\":\"learned_weight\",\"knowledge_source\":\"yuxi_graph_online\",\"yuxi_graph\":{\"entity_count\":41896,\"relationship_count\":409315},\"formulas\":[{\"id\":\"FORM-MOIST-001\",\"strategy\":\"learned_weight\"}]}", MediaType.APPLICATION_JSON));

        FormulaRecommendationResponse response = client.recommendFormulas(
                new FormulaRequest("REQ-JAVA-CLIENT", "保湿", "乳液", Collections.<String, Object>emptyMap()));

        assertEquals("REQ-JAVA-CLIENT", response.getRequestId());
        assertEquals("learned_weight", response.getStrategy());
        assertEquals("yuxi_graph_online", response.getKnowledgeSource());
        assertEquals(41896, response.getYuxiGraph().get("entity_count"));
        assertEquals("learned_weight", response.getFormulas().get(0).getStrategy());
        server.verify();
    }

    @Test
    void recordExperimentFeedbackPostsToPythonFeedbackEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000/");
        ExperimentFeedbackRequest request = new ExperimentFeedbackRequest();
        request.setFormulaId("FORM-MOIST-001");
        request.setBatchNo("BATCH-JAVA-CLIENT");
        request.setResult("pass");
        request.setIngredientIds(Arrays.asList("ING-BETAINE", "ING-PANTHENOL"));

        fixture.server.expect(requestTo("http://127.0.0.1:8000/feedback"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"formula_id\":\"FORM-MOIST-001\",\"batch_no\":\"BATCH-JAVA-CLIENT\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-BETAINE\",\"ING-PANTHENOL\"]}"))
                .andRespond(withSuccess("{\"stored\":true,\"feedback_count\":1}", MediaType.APPLICATION_JSON));

        FeedbackStoredResponse response = client.recordExperimentFeedback(request);

        assertEquals(1, response.getFeedbackCount());
        fixture.server.verify();
    }

    @Test
    void procurementPostsFormulaToPythonProcurementEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");
        FormulaCandidate formula = new FormulaCandidate(
                "FORM-MOIST-001",
                "REQ-JAVA-CLIENT",
                "保湿",
                Arrays.asList(new FormulaIngredient("ING-BETAINE", "active", BigDecimal.valueOf(0.1), BigDecimal.valueOf(3.0))),
                "reason",
                Collections.<String>emptyList(),
                Collections.<String>emptyList(),
                new FormulaScore(null, null, null, null, null, BigDecimal.valueOf(0.88)),
                "ai_recommended");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/procurement/recommend"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"formula\":{\"id\":\"FORM-MOIST-001\",\"ingredients\":[{\"ingredient_id\":\"ING-BETAINE\"}]}}"))
                .andRespond(withSuccess("{\"formula_id\":\"FORM-MOIST-001\",\"items\":[]}", MediaType.APPLICATION_JSON));

        ProcurementRecommendationResponse response = client.recommendProcurement(new ProcurementRecommendationRequest(formula));

        assertEquals("FORM-MOIST-001", response.getFormulaId());
        fixture.server.verify();
    }

    @Test
    void feedbackImpactReportPostsRequestToPythonReportEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/reports/feedback-impact"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"id\":\"REQ-REPORT-CLIENT\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andRespond(withSuccess("{\"request_id\":\"REQ-REPORT-CLIENT\",\"goal\":\"保湿\",\"feedback_count\":0,\"rows\":[]}", MediaType.APPLICATION_JSON));

        FeedbackImpactReport response = client.buildFeedbackImpactReport(
                new FormulaRequest("REQ-REPORT-CLIENT", "保湿", "乳液", Collections.<String, Object>emptyMap()));

        assertEquals("REQ-REPORT-CLIENT", response.getRequestId());
        fixture.server.verify();
    }

    @Test
    void screeningPostsDecisionToPythonScreeningEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");
        FormulaScreeningRequest request = new FormulaScreeningRequest("formula_engineer", "keep", "进入小试", Collections.<FormulaIngredient>emptyList());

        fixture.server.expect(requestTo("http://127.0.0.1:8000/screening"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().json("{\"formula_id\":\"FORM-MOIST-001\",\"engineer\":\"formula_engineer\",\"decision\":\"keep\",\"reason\":\"进入小试\",\"modified_ingredients\":[]}"))
                .andRespond(withSuccess("{\"stored\":true,\"screening_count\":1}", MediaType.APPLICATION_JSON));

        ScreeningStoredResponse response = client.recordFormulaScreening("FORM-MOIST-001", request);

        assertEquals(1, response.getScreeningCount());
        fixture.server.verify();
    }

    @Test
    void screeningListGetsPythonScreeningEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/screening?formula_id=FORM-MOIST-001"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"formula_id\":\"FORM-MOIST-001\",\"records\":[{\"formula_id\":\"FORM-MOIST-001\",\"decision\":\"keep\"}]}", MediaType.APPLICATION_JSON));

        ScreeningListResponse response = client.listFormulaScreenings("FORM-MOIST-001");

        assertEquals(1, response.getRecords().size());
        fixture.server.verify();
    }

    @Test
    void knowledgeStatusGetsPythonKnowledgeEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/knowledge/status"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"ingredient_count\":46,\"relation_count\":316,\"knowledge_source\":\"yuxi_graph_online\",\"yuxi_graph\":{\"entity_count\":41896,\"relationship_count\":409315,\"total_chunks\":13323},\"source_paths\":{\"ingredients_path\":\"data/yuxi_import/ingredients.yuxi.json\"},\"evidence_prefix_counts\":{\"YUXI\":46}}", MediaType.APPLICATION_JSON));

        KnowledgeStatusResponse response = client.getKnowledgeStatus();

        assertEquals(46, response.getIngredientCount());
        assertEquals("yuxi_graph_online", response.getKnowledgeSource());
        assertEquals(409315, response.getYuxiGraph().get("relationship_count"));
        assertEquals("data/yuxi_import/ingredients.yuxi.json", response.getSourcePaths().get("ingredients_path"));
        fixture.server.verify();
    }

    @Test
    void knowledgeGovernanceGetsPythonKnowledgeGovernanceEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/knowledge/governance"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"ingredient_count\":46,\"relation_count\":316,\"evidence_source_type_counts\":{\"ingredient_profile\":46},\"relation_type_counts\":{\"synergy\":316},\"relation_confidence_counts\":{\"medium\":316},\"ingredient_alias_count\":0,\"missing_evidence_ids\":[],\"warning_count\":1,\"warnings\":[\"cooccurrence hint\"],\"governance_notes\":[\"snapshot imports\"]}", MediaType.APPLICATION_JSON));

        KnowledgeGovernanceResponse response = client.getKnowledgeGovernance();

        assertEquals(46, response.getIngredientCount());
        assertEquals(316, response.getRelationTypeCounts().get("synergy"));
        assertEquals(1, response.getWarningCount());
        fixture.server.verify();
    }

    @Test
    void evidenceGetsPythonEvidenceEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/evidence/YUXI-ING-GLYCERIN"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"id\":\"YUXI-ING-GLYCERIN\",\"source_type\":\"ingredient_profile\",\"title\":\"Glycerin\",\"summary\":\"Classic moisturizing ingredient.\",\"source_url\":\"https://incidecoder.com/ingredients/glycerin\",\"metadata\":{\"ingredient_id\":\"ING-GLYCERIN\"}}", MediaType.APPLICATION_JSON));

        EvidenceResponse response = client.getEvidence("YUXI-ING-GLYCERIN");

        assertEquals("YUXI-ING-GLYCERIN", response.getId());
        assertEquals("ingredient_profile", response.getSourceType());
        fixture.server.verify();
    }

    @Test
    void archivedFormulaGetsPythonFormulaEndpoint() {
        RestClientFixture fixture = fixture();
        PythonFormulaAiClient client = new PythonFormulaAiClient(fixture.restTemplate, "http://127.0.0.1:8000");

        fixture.server.expect(requestTo("http://127.0.0.1:8000/formulas/FORM-MOIST-001"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"formula_id\":\"FORM-MOIST-001\",\"request_id\":\"REQ-001\",\"goal\":\"保湿\",\"formula\":{\"id\":\"FORM-MOIST-001\"}}", MediaType.APPLICATION_JSON));

        java.util.Map response = client.getArchivedFormula("FORM-MOIST-001");

        assertEquals("FORM-MOIST-001", response.get("formula_id"));
        fixture.server.verify();
    }

    private RestClientFixture fixture() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
        RestTemplate restTemplate = new RestTemplate(Collections.singletonList(new MappingJackson2HttpMessageConverter(objectMapper)));
        return new RestClientFixture(restTemplate, MockRestServiceServer.bindTo(restTemplate).build());
    }

    private static class RestClientFixture {
        private final RestTemplate restTemplate;
        private final MockRestServiceServer server;

        private RestClientFixture(RestTemplate restTemplate, MockRestServiceServer server) {
            this.restTemplate = restTemplate;
            this.server = server;
        }
    }
}
