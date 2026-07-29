package com.rjm.formulaai.management;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class ManagementApiMockMvcTests {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void healthEndpointReturnsOk() throws Exception {
        mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"));
    }

    @Test
    void knowledgeStatusEndpointReturnsLoadedKnowledgeSummary() throws Exception {
        mockMvc.perform(get("/api/knowledge/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ingredient_count").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.relation_count").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.source_paths.ingredients_path").exists());
    }

    @Test
    void knowledgeGovernanceEndpointReturnsTraceabilityAndQualitySummary() throws Exception {
        mockMvc.perform(get("/api/knowledge/governance"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ingredient_count").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.evidence_source_type_counts.ingredient_profile").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.relation_type_counts.synergy").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.relation_confidence_counts.medium").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.warning_count").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.warnings", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    void evidenceEndpointReturnsTraceableSource() throws Exception {
        mockMvc.perform(get("/api/evidence/MOCK-ING-GLYCERIN"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("MOCK-ING-GLYCERIN"))
                .andExpect(jsonPath("$.source_type").value("ingredient_profile"))
                .andExpect(jsonPath("$.source_url").exists());
    }

    @Test
    void formulaRecommendationEndpointReturnsCandidates() throws Exception {
        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-JAVA-001\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-JAVA-001"))
                .andExpect(jsonPath("$.formulas", hasSize(greaterThanOrEqualTo(1))))
                .andExpect(jsonPath("$.formulas[0].ingredients", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    void formulaArchiveEndpointReturnsStoredCandidate() throws Exception {
        mockMvc.perform(get("/api/formulas/FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.formula.id").value("FORM-MOIST-001"));
    }

    @Test
    void screeningEndpointsRecordAndListDecision() throws Exception {
        mockMvc.perform(post("/api/formulas/FORM-MOIST-001/screenings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"engineer\":\"formula_engineer\",\"decision\":\"keep\",\"reason\":\"进入小试\",\"modified_ingredients\":[]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true))
                .andExpect(jsonPath("$.screening_count").value(1));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001/screenings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.records[0].decision").value("keep"));
    }

    @Test
    void experimentFeedbackEndpointRecordsFeedback() throws Exception {
        mockMvc.perform(post("/api/experiments/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula_id\":\"FORM-MOIST-001\",\"batch_no\":\"BATCH-JAVA-001\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-BETAINE\",\"ING-PANTHENOL\"],\"metrics\":{\"stability\":\"pass\"},\"issues\":[],\"engineer\":\"lab_engineer\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true))
                .andExpect(jsonPath("$.feedback_count").value(greaterThanOrEqualTo(1)));
    }

    @Test
    void experimentBatchEndpointsCreateAndListBatches() throws Exception {
        mockMvc.perform(post("/api/experiments/batches")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"batch_no\":\"BATCH-JAVA-007\",\"formula_id\":\"FORM-MOIST-001\",\"stage\":\"lab_trial\",\"owner\":\"engineer_a\",\"metrics\":{\"hydration_after_2h\":31.5},\"issues\":[\"sticky\"],\"conclusion\":\"continue observation\",\"status\":\"running\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.batch_no").value("BATCH-JAVA-007"))
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.status").value("running"));

        mockMvc.perform(get("/api/experiments/batches")
                        .param("formula_id", "FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.batches", hasSize(greaterThanOrEqualTo(1))))
                .andExpect(jsonPath("$.batches[0].batch_no").exists());
    }

    @Test
    void procurementEndpointReturnsMatchedSkus() throws Exception {
        mockMvc.perform(post("/api/procurement/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula\":{\"id\":\"FORM-MOIST-001\",\"ingredients\":[{\"ingredient_id\":\"ING-BETAINE\",\"role\":\"active\",\"suggested_percent_min\":0.1,\"suggested_percent_max\":3.0}],\"score\":{\"overall\":0.88},\"status\":\"ai_recommended\"}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.items[0].status").value("matched"))
                .andExpect(jsonPath("$.items[0].recommended_skus", hasSize(greaterThanOrEqualTo(1))));
    }

    @Test
    void feedbackImpactReportEndpointReturnsRows() throws Exception {
        mockMvc.perform(post("/api/reports/feedback-impact")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-REPORT-JAVA\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-REPORT-JAVA"))
                .andExpect(jsonPath("$.rows", hasSize(greaterThanOrEqualTo(1))))
                .andExpect(jsonPath("$.rows[0].score_delta").exists());
    }
}
