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
import com.rjm.formulaai.management.dto.FormulaScore;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.KnowledgeGovernanceResponse;
import com.rjm.formulaai.management.dto.KnowledgeStatusResponse;
import com.rjm.formulaai.management.dto.LearnedWeightResponse;
import com.rjm.formulaai.management.dto.ProcurementItem;
import com.rjm.formulaai.management.dto.ProcurementRecommendationRequest;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.RawMaterialSkuRecommendation;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningRecord;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import com.rjm.formulaai.management.persistence.ProcurementStatusUpdateResponse;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(prefix = "rjm.ai-service", name = "mode", havingValue = "mock")
public class InMemoryFormulaAiManagementService implements FormulaAiManagementService {
    private final Map<String, List<ScreeningRecord>> screeningsByFormulaId = new ConcurrentHashMap<String, List<ScreeningRecord>>();
    private final Map<String, List<ExperimentBatchResponse>> batchesByFormulaId = new ConcurrentHashMap<String, List<ExperimentBatchResponse>>();
    private final List<ExperimentFeedbackRequest> feedbackEvents = new CopyOnWriteArrayList<ExperimentFeedbackRequest>();

    @Override
    public FormulaRecommendationResponse recommendFormulas(FormulaRequest request) {
        List<FormulaCandidate> formulas = new ArrayList<FormulaCandidate>();
        formulas.add(mockFormula("FORM-MOIST-001", request, BigDecimal.valueOf(0.886), Arrays.asList("ING-BETAINE", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE")));
        formulas.add(mockFormula("FORM-MOIST-002", request, BigDecimal.valueOf(0.814), Arrays.asList("ING-GLYCERIN", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE")));
        formulas.add(mockFormula("FORM-MOIST-003", request, BigDecimal.valueOf(0.806), Arrays.asList("ING-GLYCERIN", "ING-BETAINE", "ING-PANTHENOL")));
        return new FormulaRecommendationResponse(request.getId(), request.getGoal(), formulas);
    }

    @Override
    public AiChatResponse chat(AiChatRequest request) {
        AiChatResponse response = new AiChatResponse();
        response.setMessageId(request.getId());
        response.setKnowledgeSource("mock_mode_disabled_for_production");
        response.setAnswer("当前为 mock 测试模式，生产对话必须切换到 python 模式并连接 Yuxi 知识图谱与 AI provider。");
        return response;
    }

    @Override
    public ScreeningStoredResponse recordFormulaScreening(String formulaId, FormulaScreeningRequest request) {
        ScreeningRecord record = new ScreeningRecord(formulaId, request.getEngineer(), request.getDecision(), request.getReason(), request.getModifiedIngredients());
        if (!screeningsByFormulaId.containsKey(formulaId)) {
            screeningsByFormulaId.put(formulaId, new CopyOnWriteArrayList<ScreeningRecord>());
        }
        screeningsByFormulaId.get(formulaId).add(record);
        return new ScreeningStoredResponse(true, screeningsByFormulaId.get(formulaId).size());
    }

    @Override
    public ScreeningListResponse listFormulaScreenings(String formulaId) {
        List<ScreeningRecord> records = screeningsByFormulaId.get(formulaId);
        return new ScreeningListResponse(formulaId, records == null ? Collections.<ScreeningRecord>emptyList() : records);
    }

    @Override
    public FeedbackStoredResponse recordExperimentFeedback(ExperimentFeedbackRequest request) {
        feedbackEvents.add(request);
        return new FeedbackStoredResponse(true, feedbackEvents.size());
    }

    @Override
    public ExperimentBatchResponse createExperimentBatch(ExperimentBatchRequest request) {
        ExperimentBatchResponse response = new ExperimentBatchResponse(
                request.getBatchNo(),
                request.getFormulaId(),
                request.getStage(),
                request.getOwner(),
                request.getMetrics() == null ? Collections.<String, Object>emptyMap() : request.getMetrics(),
                request.getIssues() == null ? Collections.<String>emptyList() : request.getIssues(),
                request.getConclusion(),
                request.getStatus() == null || request.getStatus().length() == 0 ? "planned" : request.getStatus(),
                "mock://created-at");
        if (!batchesByFormulaId.containsKey(request.getFormulaId())) {
            batchesByFormulaId.put(request.getFormulaId(), new CopyOnWriteArrayList<ExperimentBatchResponse>());
        }
        batchesByFormulaId.get(request.getFormulaId()).add(0, response);
        return response;
    }

    @Override
    public ExperimentBatchListResponse listExperimentBatches(String formulaId) {
        List<ExperimentBatchResponse> batches = batchesByFormulaId.get(formulaId);
        return new ExperimentBatchListResponse(
                formulaId,
                batches == null ? Collections.<ExperimentBatchResponse>emptyList() : batches);
    }

    @Override
    public ProcurementRecommendationResponse recommendProcurement(ProcurementRecommendationRequest request) {
        List<ProcurementItem> items = new ArrayList<ProcurementItem>();
        for (FormulaIngredient ingredient : request.getFormula().getIngredients()) {
            RawMaterialSkuRecommendation sku = new RawMaterialSkuRecommendation(
                    "SKU-" + ingredient.getIngredientId(),
                    "SUP-MOCK",
                    "cosmetic grade sample",
                    price(),
                    BigDecimal.valueOf(25),
                    7,
                    Arrays.asList("COA", "MSDS"),
                    "available",
                    BigDecimal.valueOf(0.86),
                    BigDecimal.valueOf(0.851));
            items.add(new ProcurementItem(ingredient.getIngredientId(), "matched", Arrays.asList(sku)));
        }
        return new ProcurementRecommendationResponse(request.getFormula().getId(), items);
    }

    @Override
    public ProcurementRecommendationResponse listProcurementRecommendations(String formulaId) {
        return new ProcurementRecommendationResponse(formulaId, Collections.<ProcurementItem>emptyList());
    }

    @Override
    public ProcurementStatusUpdateResponse updateProcurementStatus(String formulaId, String ingredientId, String status) {
        return new ProcurementStatusUpdateResponse(false, formulaId, ingredientId, status);
    }

    @Override
    public FeedbackImpactReport buildFeedbackImpactReport(FormulaRequest request) {
        List<FeedbackImpactRow> rows = new ArrayList<FeedbackImpactRow>();
        rows.add(new FeedbackImpactRow("FORM-MOIST-001", 1, 1, BigDecimal.valueOf(0.886), BigDecimal.valueOf(0.936), BigDecimal.valueOf(0.05), Arrays.asList("ING-BETAINE", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE")));
        rows.add(new FeedbackImpactRow("FORM-MOIST-002", 2, 2, BigDecimal.valueOf(0.814), BigDecimal.valueOf(0.814), BigDecimal.ZERO, Arrays.asList("ING-GLYCERIN", "ING-PANTHENOL", "ING-SODIUM-HYALURONATE")));
        return new FeedbackImpactReport(request.getId(), request.getGoal(), feedbackEvents.size(), rows);
    }

    @Override
    public KnowledgeStatusResponse getKnowledgeStatus() {
        Map<String, String> sourcePaths = new LinkedHashMap<String, String>();
        sourcePaths.put("ingredients_path", "mock://ingredients.moisturizing.json");
        sourcePaths.put("relations_path", "mock://ingredient_relations.moisturizing.json");
        sourcePaths.put("raw_material_skus_path", "mock://raw_material_skus.json");
        sourcePaths.put("import_batch_path", "mock://import_batch.yuxi.json");

        Map<String, Integer> evidencePrefixCounts = new LinkedHashMap<String, Integer>();
        evidencePrefixCounts.put("MOCK", 5);

        return new KnowledgeStatusResponse(5, 4, 5, 5, sourcePaths, evidencePrefixCounts);
    }

    @Override
    public Map getYuxiEntityNames() {
        Map<String, String> names = new LinkedHashMap<String, String>();
        names.put("YUXI-ENT-GLYCERIN", "Glycerin");
        names.put("YUXI-ENT-PANTHENOL", "Panthenol");
        Map<String, Object> response = new LinkedHashMap<String, Object>();
        response.put("entity_names", names);
        response.put("count", names.size());
        response.put("source", "mock");
        return response;
    }

    @Override
    public KnowledgeGovernanceResponse getKnowledgeGovernance() {
        KnowledgeStatusResponse status = getKnowledgeStatus();
        Map<String, Integer> evidenceSourceTypeCounts = new LinkedHashMap<String, Integer>();
        evidenceSourceTypeCounts.put("ingredient_profile", 5);

        Map<String, Integer> relationTypeCounts = new LinkedHashMap<String, Integer>();
        relationTypeCounts.put("synergy", 4);

        Map<String, Integer> relationConfidenceCounts = new LinkedHashMap<String, Integer>();
        relationConfidenceCounts.put("medium", 4);

        return new KnowledgeGovernanceResponse(
                status.getIngredientCount(),
                status.getRelationCount(),
                status.getRawMaterialSkuCount(),
                status.getEvidenceCount(),
                status.getSourcePaths(),
                status.getEvidencePrefixCounts(),
                evidenceSourceTypeCounts,
                relationTypeCounts,
                relationConfidenceCounts,
                0,
                Collections.<String>emptyList(),
                2,
                Arrays.asList(
                        "Mock knowledge is for management-system development only.",
                        "Imported graph edges should be reviewed before production formula decisions."),
                Arrays.asList(
                        "Use Yuxi import batches as immutable knowledge snapshots.",
                        "Promote only engineer-reviewed evidence into production recommendation policies."));
    }

    @Override
    public Map getElementGraph(String elementId) {
        Map<String, Object> center = new LinkedHashMap<String, Object>();
        center.put("id", elementId);
        center.put("label", "Glycerin");
        center.put("type", "Ingredient");
        center.put("description", "Mock one-hop graph center.");

        Map<String, Object> neighbor = new LinkedHashMap<String, Object>();
        neighbor.put("id", "MOCK-PANTHENOL");
        neighbor.put("label", "Panthenol");
        neighbor.put("type", "Ingredient");
        neighbor.put("description", "Mock barrier support neighbor.");

        Map<String, Object> edge = new LinkedHashMap<String, Object>();
        edge.put("id", "MOCK-REL-1");
        edge.put("source", elementId);
        edge.put("target", "MOCK-PANTHENOL");
        edge.put("label", "synergy");
        edge.put("type", "synergy");

        Map<String, Object> stats = new LinkedHashMap<String, Object>();
        stats.put("node_count", 2);
        stats.put("edge_count", 1);
        stats.put("truncated", false);

        Map<String, Object> response = new LinkedHashMap<String, Object>();
        response.put("query", elementId);
        response.put("center", center);
        response.put("nodes", Arrays.asList(center, neighbor));
        response.put("edges", Arrays.asList(edge));
        response.put("stats", stats);
        return response;
    }

    @Override
    public EvidenceResponse getEvidence(String evidenceId) {
        Map<String, Object> metadata = new LinkedHashMap<String, Object>();
        metadata.put("ingredient_id", "ING-GLYCERIN");
        metadata.put("functions", Arrays.asList("保湿", "humectant"));
        return new EvidenceResponse(
                evidenceId,
                "ingredient_profile",
                "Glycerin",
                "Mock traceable evidence for local management-system development.",
                "mock://evidence/" + evidenceId,
                metadata);
    }

    @Override
    public Map getArchivedFormula(String formulaId) {
        FormulaRequest request = new FormulaRequest("REQ-MOCK-ARCHIVE", "保湿", "乳液", Collections.<String, Object>emptyMap());
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        row.put("formula_id", formulaId);
        row.put("request_id", request.getId());
        row.put("goal", request.getGoal());
        row.put("stored_at", "mock://stored-at");
        row.put("formula", mockFormula(formulaId, request, BigDecimal.valueOf(0.886), Arrays.asList("ING-BETAINE", "ING-PANTHENOL")));
        return row;
    }

    @Override
    public LearnedWeightResponse listLearnedWeights(String goal, String targetType) {
        return new LearnedWeightResponse(goal, targetType, Collections.emptyList());
    }

    @Override
    public FormulaLearningExplanationResponse explainFormulaLearning(String formulaId, String goal) {
        return new FormulaLearningExplanationResponse(formulaId, goal, Collections.emptyList());
    }

    private FormulaCandidate mockFormula(String id, FormulaRequest request, BigDecimal overall, List<String> ingredientIds) {
        List<FormulaIngredient> ingredients = new ArrayList<FormulaIngredient>();
        for (String ingredientId : ingredientIds) {
            ingredients.add(new FormulaIngredient(ingredientId, "active_or_supporting", BigDecimal.valueOf(0.1), BigDecimal.valueOf(3.0)));
        }
        FormulaScore score = new FormulaScore(BigDecimal.valueOf(0.9), BigDecimal.valueOf(0.7), BigDecimal.valueOf(0.8), BigDecimal.valueOf(0.75), BigDecimal.valueOf(0.75), overall);
        return new FormulaCandidate(id, request.getId(), request.getGoal(), ingredients, "mock recommendation until Python adapter is connected", Collections.<String>emptyList(), Collections.<String>emptyList(), score, "ai_recommended");
    }

    private Map<String, Object> price() {
        Map<String, Object> price = new LinkedHashMap<String, Object>();
        price.put("currency", "CNY");
        price.put("amount_per_kg", 12.5);
        return price;
    }
}
