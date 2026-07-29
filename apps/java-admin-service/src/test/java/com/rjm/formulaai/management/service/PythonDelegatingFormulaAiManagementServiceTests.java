package com.rjm.formulaai.management.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.rjm.formulaai.management.client.PythonFormulaAiClient;
import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import java.util.Collections;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class PythonDelegatingFormulaAiManagementServiceTests {
    @Test
    void delegatesAiOperationsToPythonClient() {
        PythonFormulaAiClient client = Mockito.mock(PythonFormulaAiClient.class);
        FormulaRequest request = new FormulaRequest("REQ-PY-MODE", "保湿", "乳液", Collections.<String, Object>emptyMap());
        ExperimentFeedbackRequest feedback = new ExperimentFeedbackRequest();
        ProcurementRecommendationRequest procurement = new ProcurementRecommendationRequest();

        when(client.recommendFormulas(any(FormulaRequest.class)))
                .thenReturn(new FormulaRecommendationResponse("REQ-PY-MODE", "保湿", Collections.emptyList()));
        when(client.recordExperimentFeedback(any(ExperimentFeedbackRequest.class)))
                .thenReturn(new FeedbackStoredResponse(true, 1));
        when(client.recommendProcurement(any(ProcurementRecommendationRequest.class)))
                .thenReturn(new ProcurementRecommendationResponse("FORM-MOIST-001", Collections.emptyList()));
        when(client.buildFeedbackImpactReport(any(FormulaRequest.class)))
                .thenReturn(new FeedbackImpactReport("REQ-PY-MODE", "保湿", 1, Collections.emptyList()));
        when(client.recordFormulaScreening(any(String.class), any(FormulaScreeningRequest.class)))
                .thenReturn(new ScreeningStoredResponse(true, 1));
        when(client.listFormulaScreenings(any(String.class)))
                .thenReturn(new ScreeningListResponse("FORM-MOIST-001", Collections.emptyList()));
        when(client.getKnowledgeStatus())
                .thenReturn(new KnowledgeStatusResponse(46, 316, 5, 185, Collections.<String, String>emptyMap(), Collections.<String, Integer>emptyMap()));
        when(client.getEvidence("YUXI-ING-GLYCERIN"))
                .thenReturn(new EvidenceResponse("YUXI-ING-GLYCERIN", "ingredient_profile", "Glycerin", "summary", "https://example.test", Collections.<String, Object>emptyMap()));
        when(client.getArchivedFormula("FORM-MOIST-001"))
                .thenReturn(Collections.<String, Object>singletonMap("formula_id", "FORM-MOIST-001"));

        PythonDelegatingFormulaAiManagementService service = new PythonDelegatingFormulaAiManagementService(client);

        assertEquals("REQ-PY-MODE", service.recommendFormulas(request).getRequestId());
        assertTrue(service.recordExperimentFeedback(feedback).isStored());
        assertEquals("FORM-MOIST-001", service.recommendProcurement(procurement).getFormulaId());
        assertEquals(1, service.buildFeedbackImpactReport(request).getFeedbackCount());

        FormulaScreeningRequest screening = new FormulaScreeningRequest("engineer", "keep", "进入小试", Collections.emptyList());
        ScreeningStoredResponse stored = service.recordFormulaScreening("FORM-MOIST-001", screening);
        assertTrue(stored.isStored());
        assertEquals("FORM-MOIST-001", service.listFormulaScreenings("FORM-MOIST-001").getFormulaId());
        assertEquals(46, service.getKnowledgeStatus().getIngredientCount());
        assertEquals("YUXI-ING-GLYCERIN", service.getEvidence("YUXI-ING-GLYCERIN").getId());
        assertEquals("FORM-MOIST-001", service.getArchivedFormula("FORM-MOIST-001").get("formula_id"));

        verify(client).recommendFormulas(request);
        verify(client).recordExperimentFeedback(feedback);
        verify(client).recommendProcurement(procurement);
        verify(client).buildFeedbackImpactReport(request);
        verify(client).recordFormulaScreening("FORM-MOIST-001", screening);
        verify(client).listFormulaScreenings("FORM-MOIST-001");
        verify(client).getKnowledgeStatus();
        verify(client).getEvidence("YUXI-ING-GLYCERIN");
        verify(client).getArchivedFormula("FORM-MOIST-001");
    }
}
