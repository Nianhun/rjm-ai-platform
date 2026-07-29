package com.rjm.formulaai.management.service;

import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.persistence.ExperimentFeedbackRepository;
import com.rjm.formulaai.management.persistence.FormulaCandidateArchiveRepository;
import com.rjm.formulaai.management.persistence.FormulaScreeningRepository;
import com.rjm.formulaai.management.persistence.LearnedWeightRepository;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DbArchivingFormulaAiManagementServiceTests {
    @Test
    void recommendationUsesMockLogicAndArchivesResponse() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(repository, screeningRepository, feedbackRepository);

        FormulaRequest request = new FormulaRequest(
                "REQ-DB-MODE-001",
                "moisturizing",
                "lotion",
                Collections.<String, Object>emptyMap());
        FormulaRecommendationResponse response = service.recommendFormulas(request);

        assertEquals("REQ-DB-MODE-001", response.getRequestId());
        assertEquals(3, response.getFormulas().size());
        verify(repository).saveRecommendation(response);
    }

    @Test
    void recommendationBoostsAndReranksFormulasWithPassingFeedback() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        when(feedbackRepository.countPassingByFormulaId("FORM-MOIST-002")).thenReturn(3);
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(repository, screeningRepository, feedbackRepository);

        FormulaRecommendationResponse response = service.recommendFormulas(new FormulaRequest(
                "REQ-DB-LEARN-001",
                "moisturizing",
                "lotion",
                Collections.<String, Object>emptyMap()));

        assertEquals("FORM-MOIST-002", response.getFormulas().get(0).getId());
        assertEquals("0.904", response.getFormulas().get(0).getScore().getOverall().toPlainString());
        verify(feedbackRepository).countPassingByFormulaId("FORM-MOIST-001");
        verify(feedbackRepository).countPassingByFormulaId("FORM-MOIST-002");
        verify(feedbackRepository).countPassingByFormulaId("FORM-MOIST-003");
        verify(repository).saveRecommendation(response);
    }

    @Test
    void recommendationBoostsFormulasContainingIngredientsFromPassingFeedback() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        when(feedbackRepository.countPassingByIngredientId("ING-GLYCERIN")).thenReturn(4);
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(repository, screeningRepository, feedbackRepository);

        FormulaRecommendationResponse response = service.recommendFormulas(new FormulaRequest(
                "REQ-DB-ING-LEARN-001",
                "moisturizing",
                "lotion",
                Collections.<String, Object>emptyMap()));

        assertEquals("FORM-MOIST-002", response.getFormulas().get(0).getId());
        assertEquals("0.934", response.getFormulas().get(0).getScore().getOverall().toPlainString());
        verify(feedbackRepository, atLeastOnce()).countPassingByIngredientId("ING-BETAINE");
        verify(feedbackRepository, atLeastOnce()).countPassingByIngredientId("ING-PANTHENOL");
        verify(feedbackRepository, atLeastOnce()).countPassingByIngredientId("ING-SODIUM-HYALURONATE");
        verify(feedbackRepository, atLeastOnce()).countPassingByIngredientId("ING-GLYCERIN");
        verify(repository).saveRecommendation(response);
    }

    @Test
    void recommendationBoostsFormulasContainingIngredientPairsFromPassingFeedback() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        when(feedbackRepository.countPassingByIngredientPair("ING-GLYCERIN", "ING-PANTHENOL")).thenReturn(4);
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(repository, screeningRepository, feedbackRepository);

        FormulaRecommendationResponse response = service.recommendFormulas(new FormulaRequest(
                "REQ-DB-PAIR-LEARN-001",
                "moisturizing",
                "lotion",
                Collections.<String, Object>emptyMap()));

        assertEquals("FORM-MOIST-002", response.getFormulas().get(0).getId());
        assertEquals("0.934", response.getFormulas().get(0).getScore().getOverall().toPlainString());
        verify(feedbackRepository, atLeastOnce())
                .countPassingByIngredientPair("ING-GLYCERIN", "ING-PANTHENOL");
        verify(repository).saveRecommendation(response);
    }

    @Test
    void recommendationPersistsLearnedWeightsUsedForScoreBoosting() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        LearnedWeightRepository learnedWeightRepository = mock(LearnedWeightRepository.class);
        when(feedbackRepository.countPassingByFormulaId("FORM-MOIST-002")).thenReturn(2);
        when(feedbackRepository.countPassingByIngredientId("ING-GLYCERIN")).thenReturn(3);
        when(feedbackRepository.countPassingByIngredientPair("ING-GLYCERIN", "ING-PANTHENOL")).thenReturn(4);
        DbArchivingFormulaAiManagementService service = new DbArchivingFormulaAiManagementService(
                repository, screeningRepository, feedbackRepository, learnedWeightRepository);

        service.recommendFormulas(new FormulaRequest(
                "REQ-DB-WEIGHT-AUDIT-001",
                "moisturizing",
                "lotion",
                Collections.<String, Object>emptyMap()));

        verify(learnedWeightRepository).saveWeight(
                "moisturizing",
                "formula",
                "FORM-MOIST-002",
                new BigDecimal("0.06"),
                2,
                "experiment_feedback",
                "2 passing formula feedback records");
        verify(learnedWeightRepository).saveWeight(
                "moisturizing",
                "ingredient",
                "ING-GLYCERIN",
                new BigDecimal("0.09"),
                3,
                "experiment_feedback",
                "3 passing ingredient feedback records");
        verify(learnedWeightRepository).saveWeight(
                "moisturizing",
                "ingredient_pair",
                "ING-GLYCERIN+ING-PANTHENOL",
                new BigDecimal("0.12"),
                4,
                "experiment_feedback",
                "4 passing ingredient-pair feedback records capped at 0.12");
    }

    @Test
    void archiveLookupReadsFromRepository() {
        FormulaCandidateArchiveRepository repository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        when(repository.findLatestByFormulaId("FORM-MOIST-001"))
                .thenReturn(Collections.<String, Object>singletonMap("formula_id", "FORM-MOIST-001"));
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(repository, screeningRepository, feedbackRepository);

        Map archived = service.getArchivedFormula("FORM-MOIST-001");

        assertEquals("FORM-MOIST-001", archived.get("formula_id"));
        verify(repository).findLatestByFormulaId("FORM-MOIST-001");
    }

    @Test
    void screeningWriteAndReadUseRepository() {
        FormulaCandidateArchiveRepository archiveRepository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        FormulaScreeningRequest request = new FormulaScreeningRequest(
                "engineer_a",
                "keep",
                "pilot test",
                Collections.emptyList());
        when(screeningRepository.recordScreening("FORM-MOIST-001", request))
                .thenReturn(new ScreeningStoredResponse(true, 1));
        when(screeningRepository.listScreening("FORM-MOIST-001"))
                .thenReturn(new ScreeningListResponse("FORM-MOIST-001", Collections.emptyList()));
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(archiveRepository, screeningRepository, feedbackRepository);

        assertEquals(1, service.recordFormulaScreening("FORM-MOIST-001", request).getScreeningCount());
        assertEquals("FORM-MOIST-001", service.listFormulaScreenings("FORM-MOIST-001").getFormulaId());
        verify(screeningRepository).recordScreening("FORM-MOIST-001", request);
        verify(screeningRepository).listScreening("FORM-MOIST-001");
    }

    @Test
    void experimentFeedbackUsesRepository() {
        FormulaCandidateArchiveRepository archiveRepository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        ExperimentFeedbackRequest request = new ExperimentFeedbackRequest();
        request.setFormulaId("FORM-MOIST-001");
        request.setBatchNo("BATCH-20260728-001");
        request.setResult("pass");
        request.setIngredientIds(Collections.singletonList("ING-GLYCERIN"));
        when(feedbackRepository.recordFeedback(request))
                .thenReturn(new FeedbackStoredResponse(true, 1));
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(archiveRepository, screeningRepository, feedbackRepository);

        assertEquals(1, service.recordExperimentFeedback(request).getFeedbackCount());
        verify(feedbackRepository).recordFeedback(request);
    }

    @Test
    void feedbackImpactReportCountsFeedbackForReturnedFormulaRows() {
        FormulaCandidateArchiveRepository archiveRepository = mock(FormulaCandidateArchiveRepository.class);
        FormulaScreeningRepository screeningRepository = mock(FormulaScreeningRepository.class);
        ExperimentFeedbackRepository feedbackRepository = mock(ExperimentFeedbackRepository.class);
        when(feedbackRepository.countByFormulaId("FORM-MOIST-001")).thenReturn(2);
        when(feedbackRepository.countByFormulaId("FORM-MOIST-002")).thenReturn(1);
        DbArchivingFormulaAiManagementService service =
                new DbArchivingFormulaAiManagementService(archiveRepository, screeningRepository, feedbackRepository);

        FeedbackImpactReport report = service.buildFeedbackImpactReport(
                new FormulaRequest("REQ-REPORT-DB", "moisturizing", "lotion", Collections.<String, Object>emptyMap()));

        assertEquals("REQ-REPORT-DB", report.getRequestId());
        assertEquals(3, report.getFeedbackCount());
        verify(feedbackRepository).countByFormulaId("FORM-MOIST-001");
        verify(feedbackRepository).countByFormulaId("FORM-MOIST-002");
    }
}
