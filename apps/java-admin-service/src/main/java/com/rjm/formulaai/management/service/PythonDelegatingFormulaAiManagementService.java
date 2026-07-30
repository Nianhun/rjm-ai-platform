package com.rjm.formulaai.management.service;

import com.rjm.formulaai.management.client.PythonFormulaAiClient;
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
import java.util.Collections;
import java.util.Map;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(prefix = "rjm.ai-service", name = "mode", havingValue = "python")
public class PythonDelegatingFormulaAiManagementService implements FormulaAiManagementService {
    private final PythonFormulaAiClient client;
    private final InMemoryFormulaAiManagementService localManagementDelegate = new InMemoryFormulaAiManagementService();

    public PythonDelegatingFormulaAiManagementService(PythonFormulaAiClient client) {
        this.client = client;
    }

    @Override
    public FormulaRecommendationResponse recommendFormulas(FormulaRequest request) {
        return client.recommendFormulas(request);
    }

    @Override
    public AiChatResponse chat(AiChatRequest request) {
        return client.chat(request);
    }

    @Override
    public ScreeningStoredResponse recordFormulaScreening(String formulaId, FormulaScreeningRequest request) {
        return client.recordFormulaScreening(formulaId, request);
    }

    @Override
    public ScreeningListResponse listFormulaScreenings(String formulaId) {
        return client.listFormulaScreenings(formulaId);
    }

    @Override
    public FeedbackStoredResponse recordExperimentFeedback(ExperimentFeedbackRequest request) {
        return client.recordExperimentFeedback(request);
    }

    @Override
    public ExperimentBatchResponse createExperimentBatch(ExperimentBatchRequest request) {
        return localManagementDelegate.createExperimentBatch(request);
    }

    @Override
    public ExperimentBatchListResponse listExperimentBatches(String formulaId) {
        return localManagementDelegate.listExperimentBatches(formulaId);
    }

    @Override
    public ProcurementRecommendationResponse recommendProcurement(ProcurementRecommendationRequest request) {
        return client.recommendProcurement(request);
    }

    @Override
    public ProcurementRecommendationResponse listProcurementRecommendations(String formulaId) {
        return new ProcurementRecommendationResponse(formulaId, Collections.emptyList());
    }

    @Override
    public ProcurementStatusUpdateResponse updateProcurementStatus(String formulaId, String ingredientId, String status) {
        return new ProcurementStatusUpdateResponse(false, formulaId, ingredientId, status);
    }

    @Override
    public FeedbackImpactReport buildFeedbackImpactReport(FormulaRequest request) {
        return client.buildFeedbackImpactReport(request);
    }

    @Override
    public KnowledgeStatusResponse getKnowledgeStatus() {
        return client.getKnowledgeStatus();
    }

    @Override
    public KnowledgeGovernanceResponse getKnowledgeGovernance() {
        return client.getKnowledgeGovernance();
    }

    @Override
    public EvidenceResponse getEvidence(String evidenceId) {
        return client.getEvidence(evidenceId);
    }

    @Override
    public Map getArchivedFormula(String formulaId) {
        return client.getArchivedFormula(formulaId);
    }

    @Override
    public LearnedWeightResponse listLearnedWeights(String goal, String targetType) {
        return new LearnedWeightResponse(goal, targetType, Collections.emptyList());
    }

    @Override
    public FormulaLearningExplanationResponse explainFormulaLearning(String formulaId, String goal) {
        return new FormulaLearningExplanationResponse(formulaId, goal, Collections.emptyList());
    }
}
