package com.rjm.formulaai.management.service;

import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchListResponse;
import com.rjm.formulaai.management.dto.ExperimentBatchRequest;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;
import com.rjm.formulaai.management.dto.EvidenceResponse;
import com.rjm.formulaai.management.dto.FeedbackImpactReport;
import com.rjm.formulaai.management.dto.FeedbackImpactRow;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import com.rjm.formulaai.management.dto.FormulaCandidate;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaLearningExplanationResponse;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaRequest;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.LearnedWeightResponse;
import com.rjm.formulaai.management.dto.LearnedWeightRow;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.persistence.ExperimentFeedbackRepository;
import com.rjm.formulaai.management.persistence.ExperimentBatchRepository;
import com.rjm.formulaai.management.persistence.FormulaCandidateArchiveRepository;
import com.rjm.formulaai.management.persistence.FormulaScreeningRepository;
import com.rjm.formulaai.management.persistence.LearnedWeightRecord;
import com.rjm.formulaai.management.persistence.LearnedWeightRepository;
import com.rjm.formulaai.management.persistence.ProcurementRecommendationRepository;
import com.rjm.formulaai.management.persistence.ProcurementStatusUpdateResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
@ConditionalOnProperty(prefix = "rjm.ai-service", name = "mode", havingValue = "db")
public class DbArchivingFormulaAiManagementService implements FormulaAiManagementService {
    private final FormulaCandidateArchiveRepository archiveRepository;
    private final FormulaScreeningRepository screeningRepository;
    private final ExperimentFeedbackRepository feedbackRepository;
    private final ExperimentBatchRepository experimentBatchRepository;
    private final LearnedWeightRepository learnedWeightRepository;
    private final ProcurementRecommendationRepository procurementRepository;
    private final InMemoryFormulaAiManagementService delegate = new InMemoryFormulaAiManagementService();

    public DbArchivingFormulaAiManagementService(
            FormulaCandidateArchiveRepository archiveRepository,
            FormulaScreeningRepository screeningRepository,
            ExperimentFeedbackRepository feedbackRepository) {
        this(archiveRepository, screeningRepository, feedbackRepository, null, null, null);
    }

    @Autowired
    public DbArchivingFormulaAiManagementService(
            FormulaCandidateArchiveRepository archiveRepository,
            FormulaScreeningRepository screeningRepository,
            ExperimentFeedbackRepository feedbackRepository,
            LearnedWeightRepository learnedWeightRepository,
            ProcurementRecommendationRepository procurementRepository,
            ExperimentBatchRepository experimentBatchRepository) {
        this.archiveRepository = archiveRepository;
        this.screeningRepository = screeningRepository;
        this.feedbackRepository = feedbackRepository;
        this.experimentBatchRepository = experimentBatchRepository;
        this.learnedWeightRepository = learnedWeightRepository;
        this.procurementRepository = procurementRepository;
    }

    public DbArchivingFormulaAiManagementService(
            FormulaCandidateArchiveRepository archiveRepository,
            FormulaScreeningRepository screeningRepository,
            ExperimentFeedbackRepository feedbackRepository,
            LearnedWeightRepository learnedWeightRepository) {
        this(archiveRepository, screeningRepository, feedbackRepository, learnedWeightRepository, null, null);
    }

    @Override
    public FormulaRecommendationResponse recommendFormulas(FormulaRequest request) {
        FormulaRecommendationResponse response = delegate.recommendFormulas(request);
        applyPassingFeedbackBoost(response);
        archiveRepository.saveRecommendation(response);
        return response;
    }

    @Override
    public AiChatResponse chat(AiChatRequest request) {
        return delegate.chat(request);
    }

    @Override
    public ScreeningStoredResponse recordFormulaScreening(String formulaId, FormulaScreeningRequest request) {
        return screeningRepository.recordScreening(formulaId, request);
    }

    @Override
    public ScreeningListResponse listFormulaScreenings(String formulaId) {
        return screeningRepository.listScreening(formulaId);
    }

    @Override
    public FeedbackStoredResponse recordExperimentFeedback(ExperimentFeedbackRequest request) {
        return feedbackRepository.recordFeedback(request);
    }

    @Override
    public ExperimentBatchResponse createExperimentBatch(ExperimentBatchRequest request) {
        if (experimentBatchRepository == null) {
            return delegate.createExperimentBatch(request);
        }
        return experimentBatchRepository.createBatch(request);
    }

    @Override
    public ExperimentBatchListResponse listExperimentBatches(String formulaId) {
        if (experimentBatchRepository == null) {
            return delegate.listExperimentBatches(formulaId);
        }
        return new ExperimentBatchListResponse(formulaId, experimentBatchRepository.listBatchesByFormula(formulaId));
    }

    @Override
    public ProcurementRecommendationResponse recommendProcurement(ProcurementRecommendationRequest request) {
        ProcurementRecommendationResponse response = delegate.recommendProcurement(request);
        if (procurementRepository != null) {
            procurementRepository.saveRecommendation(response);
        }
        return response;
    }

    @Override
    public ProcurementRecommendationResponse listProcurementRecommendations(String formulaId) {
        if (procurementRepository == null) {
            return delegate.listProcurementRecommendations(formulaId);
        }
        return procurementRepository.listRecommendations(formulaId);
    }

    @Override
    public ProcurementStatusUpdateResponse updateProcurementStatus(String formulaId, String ingredientId, String status) {
        if (procurementRepository == null) {
            return delegate.updateProcurementStatus(formulaId, ingredientId, status);
        }
        return procurementRepository.updateStatus(formulaId, ingredientId, status);
    }

    @Override
    public FeedbackImpactReport buildFeedbackImpactReport(FormulaRequest request) {
        FeedbackImpactReport report = delegate.buildFeedbackImpactReport(request);
        int feedbackCount = 0;
        for (FeedbackImpactRow row : report.getRows()) {
            feedbackCount += feedbackRepository.countByFormulaId(row.getFormulaId());
        }
        report.setFeedbackCount(feedbackCount);
        return report;
    }

    @Override
    public KnowledgeStatusResponse getKnowledgeStatus() {
        return delegate.getKnowledgeStatus();
    }

    @Override
    public Map getYuxiEntityNames() {
        return delegate.getYuxiEntityNames();
    }

    @Override
    public KnowledgeGovernanceResponse getKnowledgeGovernance() {
        return delegate.getKnowledgeGovernance();
    }

    @Override
    public Map getElementGraph(String elementId) {
        return delegate.getElementGraph(elementId);
    }

    @Override
    public EvidenceResponse getEvidence(String evidenceId) {
        return delegate.getEvidence(evidenceId);
    }

    @Override
    public Map getArchivedFormula(String formulaId) {
        return archiveRepository.findLatestByFormulaId(formulaId);
    }

    @Override
    public LearnedWeightResponse listLearnedWeights(String goal, String targetType) {
        if (learnedWeightRepository == null) {
            return new LearnedWeightResponse(goal, targetType, Collections.<LearnedWeightRow>emptyList());
        }
        List<LearnedWeightRow> rows = new ArrayList<LearnedWeightRow>();
        for (LearnedWeightRecord record : learnedWeightRepository.listWeights(goal, targetType)) {
            rows.add(new LearnedWeightRow(
                    record.getGoal(),
                    record.getTargetType(),
                    record.getTargetKey(),
                    record.getWeight(),
                    record.getEvidenceCount(),
                    record.getSource(),
                    record.getCalculationNote()));
        }
        return new LearnedWeightResponse(goal, targetType, rows);
    }

    @Override
    public FormulaLearningExplanationResponse explainFormulaLearning(String formulaId, String goal) {
        Set<String> ingredientIds = ingredientIdsFromArchivedFormula(formulaId);
        List<LearnedWeightRow> influences = new ArrayList<LearnedWeightRow>();
        for (LearnedWeightRow row : listLearnedWeights(goal, "formula").getWeights()) {
            if (formulaId.equals(row.getTargetKey())) {
                influences.add(row);
            }
        }
        for (LearnedWeightRow row : listLearnedWeights(goal, "ingredient").getWeights()) {
            if (ingredientIds.contains(row.getTargetKey())) {
                influences.add(row);
            }
        }
        for (LearnedWeightRow row : listLearnedWeights(goal, "ingredient_pair").getWeights()) {
            String[] pair = row.getTargetKey().split("\\+");
            if (pair.length == 2 && ingredientIds.contains(pair[0]) && ingredientIds.contains(pair[1])) {
                influences.add(row);
            }
        }
        Collections.sort(influences, new Comparator<LearnedWeightRow>() {
            @Override
            public int compare(LearnedWeightRow left, LearnedWeightRow right) {
                return right.getWeight().compareTo(left.getWeight());
            }
        });
        return new FormulaLearningExplanationResponse(formulaId, goal, influences);
    }

    private void applyPassingFeedbackBoost(FormulaRecommendationResponse response) {
        Set<String> savedWeightKeys = new HashSet<String>();
        for (FormulaCandidate formula : response.getFormulas()) {
            int passingFeedbackCount = feedbackRepository.countPassingByFormulaId(formula.getId());
            if (passingFeedbackCount <= 0 || formula.getScore() == null || formula.getScore().getOverall() == null) {
                continue;
            }
            BigDecimal boost = BigDecimal.valueOf(Math.min(passingFeedbackCount, 4))
                    .multiply(BigDecimal.valueOf(0.03));
            formula.getScore().setOverall(formula.getScore().getOverall().add(boost));
            saveLearnedWeight(savedWeightKeys, response.getGoal(), "formula", formula.getId(), boost, passingFeedbackCount,
                    passingFeedbackCount + " passing formula feedback records");
        }
        for (FormulaCandidate formula : response.getFormulas()) {
            if (formula.getScore() == null || formula.getScore().getOverall() == null) {
                continue;
            }
            BigDecimal ingredientBoost = BigDecimal.ZERO;
            for (FormulaIngredient ingredient : formula.getIngredients()) {
                int passingIngredientCount =
                        feedbackRepository.countPassingByIngredientId(ingredient.getIngredientId());
                BigDecimal currentBoost = BigDecimal.valueOf(Math.min(passingIngredientCount, 4))
                        .multiply(BigDecimal.valueOf(0.03));
                ingredientBoost = ingredientBoost.add(currentBoost);
                if (passingIngredientCount > 0) {
                    saveLearnedWeight(savedWeightKeys, response.getGoal(), "ingredient", ingredient.getIngredientId(),
                            currentBoost,
                            passingIngredientCount,
                            passingIngredientCount + " passing ingredient feedback records");
                }
            }
            if (ingredientBoost.compareTo(BigDecimal.valueOf(0.12)) > 0) {
                ingredientBoost = BigDecimal.valueOf(0.12);
            }
            formula.getScore().setOverall(formula.getScore().getOverall().add(ingredientBoost));
        }
        for (FormulaCandidate formula : response.getFormulas()) {
            if (formula.getScore() == null || formula.getScore().getOverall() == null) {
                continue;
            }
            BigDecimal pairBoost = BigDecimal.ZERO;
            for (int left = 0; left < formula.getIngredients().size(); left++) {
                for (int right = left + 1; right < formula.getIngredients().size(); right++) {
                    int passingPairCount = feedbackRepository.countPassingByIngredientPair(
                            formula.getIngredients().get(left).getIngredientId(),
                            formula.getIngredients().get(right).getIngredientId());
                    BigDecimal currentBoost = BigDecimal.valueOf(Math.min(passingPairCount, 4))
                            .multiply(BigDecimal.valueOf(0.03));
                    pairBoost = pairBoost.add(currentBoost);
                    if (passingPairCount > 0) {
                        saveLearnedWeight(savedWeightKeys, response.getGoal(), "ingredient_pair",
                                formula.getIngredients().get(left).getIngredientId() + "+"
                                        + formula.getIngredients().get(right).getIngredientId(),
                                currentBoost,
                                passingPairCount,
                                passingPairCount + " passing ingredient-pair feedback records capped at 0.12");
                    }
                }
            }
            if (pairBoost.compareTo(BigDecimal.valueOf(0.12)) > 0) {
                pairBoost = BigDecimal.valueOf(0.12);
            }
            formula.getScore().setOverall(formula.getScore().getOverall().add(pairBoost));
        }
        Collections.sort(response.getFormulas(), new Comparator<FormulaCandidate>() {
            @Override
            public int compare(FormulaCandidate left, FormulaCandidate right) {
                BigDecimal leftScore = left.getScore() == null ? BigDecimal.ZERO : left.getScore().getOverall();
                BigDecimal rightScore = right.getScore() == null ? BigDecimal.ZERO : right.getScore().getOverall();
                return rightScore.compareTo(leftScore);
            }
        });
    }

    private void saveLearnedWeight(Set<String> savedWeightKeys, String goal, String targetType, String targetKey,
            BigDecimal weight,
            int evidenceCount, String calculationNote) {
        if (learnedWeightRepository == null) {
            return;
        }
        String uniqueKey = goal + "|" + targetType + "|" + targetKey;
        if (!savedWeightKeys.add(uniqueKey)) {
            return;
        }
        learnedWeightRepository.saveWeight(goal, targetType, targetKey, weight, evidenceCount,
                "experiment_feedback", calculationNote);
    }

    private Set<String> ingredientIdsFromArchivedFormula(String formulaId) {
        Set<String> ingredientIds = new LinkedHashSet<String>();
        Map archived = archiveRepository.findLatestByFormulaId(formulaId);
        if (archived == null) {
            return ingredientIds;
        }
        Object formula = archived.get("formula");
        if (!(formula instanceof Map)) {
            return ingredientIds;
        }
        Object ingredients = ((Map) formula).get("ingredients");
        if (!(ingredients instanceof List)) {
            return ingredientIds;
        }
        for (Object ingredient : (List) ingredients) {
            if (ingredient instanceof Map) {
                Object ingredientId = ((Map) ingredient).get("ingredient_id");
                if (ingredientId != null) {
                    ingredientIds.add(String.valueOf(ingredientId));
                }
            }
        }
        return ingredientIds;
    }
}
