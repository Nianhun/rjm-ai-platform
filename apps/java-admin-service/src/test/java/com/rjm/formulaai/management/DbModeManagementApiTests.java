package com.rjm.formulaai.management;

import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchListResponse;
import com.rjm.formulaai.management.persistence.ExperimentBatchRepository;
import com.rjm.formulaai.management.persistence.ExperimentFeedbackRepository;
import com.rjm.formulaai.management.persistence.FormulaCandidateArchiveRepository;
import com.rjm.formulaai.management.persistence.FormulaScreeningRepository;
import com.rjm.formulaai.management.persistence.LearnedWeightRepository;
import com.rjm.formulaai.management.persistence.ProcurementRecommendationRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Collections;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = "rjm.ai-service.mode=db")
@AutoConfigureMockMvc
class DbModeManagementApiTests {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private FormulaCandidateArchiveRepository archiveRepository;

    @MockBean
    private FormulaScreeningRepository screeningRepository;

    @MockBean
    private ExperimentFeedbackRepository feedbackRepository;

    @MockBean
    private LearnedWeightRepository learnedWeightRepository;

    @MockBean
    private ProcurementRecommendationRepository procurementRecommendationRepository;

    @MockBean
    private ExperimentBatchRepository experimentBatchRepository;

    @Test
    void dbModeArchivesRecommendationAndReadsArchivedFormula() throws Exception {
        when(archiveRepository.findLatestByFormulaId("FORM-MOIST-001"))
                .thenReturn(Collections.<String, Object>singletonMap("formula_id", "FORM-MOIST-001"));

        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-DB-MODE-API\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-DB-MODE-API"))
                .andExpect(jsonPath("$.formulas[0].id").value("FORM-MOIST-001"));
        verify(archiveRepository).saveRecommendation(any());

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"));
    }

    @Test
    void dbModeRecordsExperimentFeedbackThroughRepository() throws Exception {
        when(feedbackRepository.recordFeedback(any()))
                .thenReturn(new FeedbackStoredResponse(true, 1));

        mockMvc.perform(post("/api/experiments/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula_id\":\"FORM-MOIST-001\",\"batch_no\":\"BATCH-001\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-GLYCERIN\"]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true))
                .andExpect(jsonPath("$.feedback_count").value(1));
        verify(feedbackRepository).recordFeedback(any());
    }

    @Test
    void dbModeCreatesAndListsExperimentBatchesThroughRepository() throws Exception {
        when(experimentBatchRepository.createBatch(any()))
                .thenReturn(new ExperimentBatchResponse(
                        "BATCH-DB-007",
                        "FORM-MOIST-001",
                        "lab_trial",
                        "engineer_a",
                        Collections.<String, Object>singletonMap("hydration_after_2h", 31.5),
                        Collections.singletonList("sticky"),
                        "continue observation",
                        "running",
                        "2026-07-28 14:00:00"));
        when(experimentBatchRepository.listBatchesByFormula("FORM-MOIST-001"))
                .thenReturn(Collections.singletonList(new ExperimentBatchResponse(
                        "BATCH-DB-007",
                        "FORM-MOIST-001",
                        "lab_trial",
                        "engineer_a",
                        Collections.<String, Object>emptyMap(),
                        Collections.<String>emptyList(),
                        "continue observation",
                        "running",
                        "2026-07-28 14:00:00")));

        mockMvc.perform(post("/api/experiments/batches")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"batch_no\":\"BATCH-DB-007\",\"formula_id\":\"FORM-MOIST-001\",\"stage\":\"lab_trial\",\"owner\":\"engineer_a\",\"metrics\":{\"hydration_after_2h\":31.5},\"issues\":[\"sticky\"],\"conclusion\":\"continue observation\",\"status\":\"running\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.batch_no").value("BATCH-DB-007"))
                .andExpect(jsonPath("$.status").value("running"));
        verify(experimentBatchRepository).createBatch(any());

        mockMvc.perform(get("/api/experiments/batches")
                        .param("formula_id", "FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.batches[0].batch_no").value("BATCH-DB-007"));
        verify(experimentBatchRepository).listBatchesByFormula("FORM-MOIST-001");
    }

    @Test
    void dbModeFeedbackImpactReportCountsFeedbackThroughRepository() throws Exception {
        when(feedbackRepository.countByFormulaId("FORM-MOIST-001")).thenReturn(2);
        when(feedbackRepository.countByFormulaId("FORM-MOIST-002")).thenReturn(1);

        mockMvc.perform(post("/api/reports/feedback-impact")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-REPORT-DB-API\",\"goal\":\"moisturizing\",\"dosage_form\":\"lotion\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-REPORT-DB-API"))
                .andExpect(jsonPath("$.feedback_count").value(3));
        verify(feedbackRepository).countByFormulaId("FORM-MOIST-001");
        verify(feedbackRepository).countByFormulaId("FORM-MOIST-002");
    }
}
