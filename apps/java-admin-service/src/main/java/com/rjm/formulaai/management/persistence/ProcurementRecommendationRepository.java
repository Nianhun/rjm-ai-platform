package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ProcurementItem;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.RawMaterialSkuRecommendation;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class ProcurementRecommendationRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public ProcurementRecommendationRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public void saveRecommendation(ProcurementRecommendationResponse response) {
        for (ProcurementItem item : response.getItems()) {
            if (item.getRecommendedSkus() == null || item.getRecommendedSkus().isEmpty()) {
                insertRecommendation(response.getFormulaId(), item.getIngredientId(), item.getStatus(), null);
                continue;
            }
            for (RawMaterialSkuRecommendation sku : item.getRecommendedSkus()) {
                saveSku(item.getIngredientId(), sku);
                insertRecommendation(response.getFormulaId(), item.getIngredientId(), item.getStatus(), sku);
            }
        }
    }

    public ProcurementRecommendationResponse listRecommendations(String formulaId) {
        List<ProcurementItem> items = new ArrayList<ProcurementItem>();
        try {
            Connection connection = dataSource.getConnection();
            try {
                PreparedStatement statement = connection.prepareStatement(
                        "select ingredient_id, status, recommendation_json from procurement_recommendation "
                                + "where formula_id = ? order by id");
                try {
                    statement.setString(1, formulaId);
                    ResultSet rows = statement.executeQuery();
                    try {
                        while (rows.next()) {
                            RawMaterialSkuRecommendation sku = readSku(rows.getString("recommendation_json"));
                            List<RawMaterialSkuRecommendation> skus = sku == null
                                    ? Collections.<RawMaterialSkuRecommendation>emptyList()
                                    : Collections.singletonList(sku);
                            items.add(new ProcurementItem(
                                    rows.getString("ingredient_id"),
                                    rows.getString("status"),
                                    skus));
                        }
                    } finally {
                        rows.close();
                    }
                } finally {
                    statement.close();
                }
            } finally {
                connection.close();
            }
        } catch (Exception error) {
            throw new IllegalStateException("Failed to list procurement recommendations", error);
        }
        return new ProcurementRecommendationResponse(formulaId, items);
    }

    public ProcurementStatusUpdateResponse updateStatus(String formulaId, String ingredientId, String status) {
        try {
            Connection connection = dataSource.getConnection();
            try {
                PreparedStatement statement = connection.prepareStatement(
                        "update procurement_recommendation set status = ? where formula_id = ? and ingredient_id = ?");
                try {
                    statement.setString(1, status);
                    statement.setString(2, formulaId);
                    statement.setString(3, ingredientId);
                    int updated = statement.executeUpdate();
                    return new ProcurementStatusUpdateResponse(updated > 0, formulaId, ingredientId, status);
                } finally {
                    statement.close();
                }
            } finally {
                connection.close();
            }
        } catch (Exception error) {
            throw new IllegalStateException("Failed to update procurement recommendation status", error);
        }
    }

    private void saveSku(String ingredientId, RawMaterialSkuRecommendation sku) {
        if (sku.getSkuId() == null) {
            return;
        }
        try {
            Connection connection = dataSource.getConnection();
            try {
                PreparedStatement statement = connection.prepareStatement(
                        "update raw_material_sku set ingredient_id = ?, supplier_id = ?, supplier_name = ?, "
                                + "specification = ?, price_currency = ?, price_amount_per_kg = ?, moq_kg = ?, "
                                + "lead_time_days = ?, qualification_files_json = ?, sample_status = ?, quality_rating = ? "
                                + "where sku_id = ?");
                try {
                    bindSkuUpdate(statement, ingredientId, sku);
                    if (statement.executeUpdate() > 0) {
                        return;
                    }
                } finally {
                    statement.close();
                }
                PreparedStatement insert = connection.prepareStatement(
                        "insert into raw_material_sku "
                                + "(sku_id, ingredient_id, supplier_id, supplier_name, specification, price_currency, "
                                + "price_amount_per_kg, moq_kg, lead_time_days, qualification_files_json, sample_status, quality_rating) "
                                + "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
                try {
                    Map<String, Object> price = sku.getPrice();
                    insert.setString(1, sku.getSkuId());
                    insert.setString(2, ingredientId);
                    insert.setString(3, sku.getSupplierId());
                    insert.setString(4, sku.getSupplierId());
                    insert.setString(5, sku.getSpecification());
                    insert.setString(6, stringValue(price, "currency"));
                    insert.setBigDecimal(7, decimalValue(price, "amount_per_kg"));
                    insert.setBigDecimal(8, sku.getMoqKg());
                    insert.setInt(9, sku.getLeadTimeDays());
                    insert.setString(10, objectMapper.writeValueAsString(sku.getQualificationFiles()));
                    insert.setString(11, sku.getSampleStatus());
                    insert.setBigDecimal(12, sku.getQualityRating());
                    insert.executeUpdate();
                } finally {
                    insert.close();
                }
            } finally {
                connection.close();
            }
        } catch (Exception error) {
            throw new IllegalStateException("Failed to save raw material SKU", error);
        }
    }

    private void bindSkuUpdate(PreparedStatement statement, String ingredientId, RawMaterialSkuRecommendation sku)
            throws Exception {
        Map<String, Object> price = sku.getPrice();
        statement.setString(1, ingredientId);
        statement.setString(2, sku.getSupplierId());
        statement.setString(3, sku.getSupplierId());
        statement.setString(4, sku.getSpecification());
        statement.setString(5, stringValue(price, "currency"));
        statement.setBigDecimal(6, decimalValue(price, "amount_per_kg"));
        statement.setBigDecimal(7, sku.getMoqKg());
        statement.setInt(8, sku.getLeadTimeDays());
        statement.setString(9, objectMapper.writeValueAsString(sku.getQualificationFiles()));
        statement.setString(10, sku.getSampleStatus());
        statement.setBigDecimal(11, sku.getQualityRating());
        statement.setString(12, sku.getSkuId());
    }

    private void insertRecommendation(String formulaId, String ingredientId, String status,
            RawMaterialSkuRecommendation sku) {
        try {
            Connection connection = dataSource.getConnection();
            try {
                PreparedStatement statement = connection.prepareStatement(
                        "insert into procurement_recommendation "
                                + "(formula_id, ingredient_id, sku_id, supplier_id, status, procurement_score, recommendation_json) "
                                + "values (?, ?, ?, ?, ?, ?, ?)");
                try {
                    statement.setString(1, formulaId);
                    statement.setString(2, ingredientId);
                    statement.setString(3, sku == null ? null : sku.getSkuId());
                    statement.setString(4, sku == null ? null : sku.getSupplierId());
                    statement.setString(5, status);
                    statement.setBigDecimal(6, sku == null ? null : sku.getProcurementScore());
                    statement.setString(7, sku == null ? "{}" : objectMapper.writeValueAsString(sku));
                    statement.executeUpdate();
                } finally {
                    statement.close();
                }
            } finally {
                connection.close();
            }
        } catch (Exception error) {
            throw new IllegalStateException("Failed to save procurement recommendation", error);
        }
    }

    private RawMaterialSkuRecommendation readSku(String json) throws Exception {
        Map<String, Object> raw = objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {
        });
        if (raw.isEmpty()) {
            return null;
        }
        return objectMapper.convertValue(raw, RawMaterialSkuRecommendation.class);
    }

    private String stringValue(Map<String, Object> values, String key) {
        Object value = values == null ? null : values.get(key);
        return value == null ? null : String.valueOf(value);
    }

    private java.math.BigDecimal decimalValue(Map<String, Object> values, String key) {
        Object value = values == null ? null : values.get(key);
        if (value == null) {
            return null;
        }
        return new java.math.BigDecimal(String.valueOf(value));
    }
}
