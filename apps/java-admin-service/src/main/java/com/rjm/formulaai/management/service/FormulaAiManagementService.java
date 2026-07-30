package com.rjm.formulaai.management.service;

import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchListResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchRequest;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;
import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaLearningExplanationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.LearnedWeightResponse;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.persistence.ProcurementStatusUpdateResponse;
import java.util.Map;

public interface FormulaAiManagementService {
    FormulaRecommendationResponse recommendFormulas(FormulaRequest request);

    AiChatResponse chat(AiChatRequest request);

    ScreeningStoredResponse recordFormulaScreening(String formulaId, FormulaScreeningRequest request);

    ScreeningListResponse listFormulaScreenings(String formulaId);

    FeedbackStoredResponse recordExperimentFeedback(ExperimentFeedbackRequest request);

    ExperimentBatchResponse createExperimentBatch(ExperimentBatchRequest request);

    ExperimentBatchListResponse listExperimentBatches(String formulaId);

    ProcurementRecommendationResponse recommendProcurement(ProcurementRecommendationRequest request);

    ProcurementRecommendationResponse listProcurementRecommendations(String formulaId);

    ProcurementStatusUpdateResponse updateProcurementStatus(String formulaId, String ingredientId, String status);

    FeedbackImpactReport buildFeedbackImpactReport(FormulaRequest request);

    KnowledgeStatusResponse getKnowledgeStatus();

    KnowledgeGovernanceResponse getKnowledgeGovernance();

    EvidenceResponse getEvidence(String evidenceId);

    Map getArchivedFormula(String formulaId);

    LearnedWeightResponse listLearnedWeights(String goal, String targetType);

    FormulaLearningExplanationResponse explainFormulaLearning(String formulaId, String goal);
}
