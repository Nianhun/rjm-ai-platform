package com.rjm.formulaai.management;

import com.rjm.formulaai.management.persistence.ExperimentFeedbackRepository;
import com.rjm.formulaai.management.persistence.ExperimentBatchRepository;
import com.rjm.formulaai.management.persistence.FormulaCandidateArchiveRepository;
import com.rjm.formulaai.management.persistence.FormulaScreeningRepository;
import com.rjm.formulaai.management.persistence.LearnedWeightRecord;
import com.rjm.formulaai.management.persistence.LearnedWeightRepository;
import com.rjm.formulaai.management.persistence.ProcurementRecommendationRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = {"rjm.ai-service.mode=db", "rjm.auth.enabled=false"})
@AutoConfigureMockMvc
class LearningControllerTests {
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
    void learnedWeightsEndpointReturnsAuditableWeightRows() throws Exception {
        when(learnedWeightRepository.listWeights("moisturizing", "ingredient_pair"))
                .thenReturn(Collections.singletonList(new LearnedWeightRecord(
                        "moisturizing",
                        "ingredient_pair",
                        "ING-GLYCERIN+ING-PANTHENOL",
                        new BigDecimal("0.12"),
                        4,
                        "experiment_feedback",
                        "4 passing ingredient-pair feedback records capped at 0.12")));

        mockMvc.perform(get("/api/learning/weights")
                        .param("goal", "moisturizing")
                        .param("target_type", "ingredient_pair"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.goal").value("moisturizing"))
                .andExpect(jsonPath("$.target_type").value("ingredient_pair"))
                .andExpect(jsonPath("$.weights[0].target_key").value("ING-GLYCERIN+ING-PANTHENOL"))
                .andExpect(jsonPath("$.weights[0].weight").value(0.12))
                .andExpect(jsonPath("$.weights[0].evidence_count").value(4))
                .andExpect(jsonPath("$.weights[0].source").value("experiment_feedback"))
                .andExpect(jsonPath("$.weights[0].calculation_note")
                        .value("4 passing ingredient-pair feedback records capped at 0.12"));

        verify(learnedWeightRepository).listWeights("moisturizing", "ingredient_pair");
    }

    @Test
    void formulaExplanationEndpointReturnsWeightsRelevantToArchivedFormula() throws Exception {
        Map<String, Object> glycerin = new LinkedHashMap<String, Object>();
        glycerin.put("ingredient_id", "ING-GLYCERIN");
        Map<String, Object> panthenol = new LinkedHashMap<String, Object>();
        panthenol.put("ingredient_id", "ING-PANTHENOL");
        Map<String, Object> formula = new LinkedHashMap<String, Object>();
        formula.put("id", "FORM-MOIST-002");
        formula.put("ingredients", Arrays.asList(glycerin, panthenol));
        Map<String, Object> archived = new LinkedHashMap<String, Object>();
        archived.put("formula_id", "FORM-MOIST-002");
        archived.put("formula", formula);
        when(archiveRepository.findLatestByFormulaId("FORM-MOIST-002")).thenReturn(archived);
        when(learnedWeightRepository.listWeights("moisturizing", "formula"))
                .thenReturn(Collections.singletonList(new LearnedWeightRecord(
                        "moisturizing", "formula", "FORM-MOIST-002", new BigDecimal("0.06"),
                        2, "experiment_feedback", "2 passing formula feedback records")));
        when(learnedWeightRepository.listWeights("moisturizing", "ingredient"))
                .thenReturn(Collections.singletonList(new LearnedWeightRecord(
                        "moisturizing", "ingredient", "ING-GLYCERIN", new BigDecimal("0.09"),
                        3, "experiment_feedback", "3 passing ingredient feedback records")));
        when(learnedWeightRepository.listWeights("moisturizing", "ingredient_pair"))
                .thenReturn(Collections.singletonList(new LearnedWeightRecord(
                        "moisturizing", "ingredient_pair", "ING-GLYCERIN+ING-PANTHENOL", new BigDecimal("0.12"),
                        4, "experiment_feedback", "4 passing ingredient-pair feedback records capped at 0.12")));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-002/explanation")
                        .param("goal", "moisturizing"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-002"))
                .andExpect(jsonPath("$.goal").value("moisturizing"))
                .andExpect(jsonPath("$.influences[0].target_type").value("ingredient_pair"))
                .andExpect(jsonPath("$.influences[0].target_key").value("ING-GLYCERIN+ING-PANTHENOL"))
                .andExpect(jsonPath("$.influences[0].weight").value(0.12))
                .andExpect(jsonPath("$.influences[1].target_type").value("ingredient"))
                .andExpect(jsonPath("$.influences[2].target_type").value("formula"));

        verify(archiveRepository).findLatestByFormulaId("FORM-MOIST-002");
    }
}
