package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.FormulaCandidate;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class FormulaCandidateArchiveRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public FormulaCandidateArchiveRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public void saveRecommendation(FormulaRecommendationResponse response) {
        Connection connection = null;
        try {
            connection = dataSource.getConnection();
            connection.setAutoCommit(false);
            saveRequest(connection, response);
            for (FormulaCandidate formula : safeFormulas(response)) {
                saveCandidate(connection, response, formula);
            }
            connection.commit();
        } catch (Exception exception) {
            rollbackQuietly(connection);
            throw new IllegalStateException("Failed to archive formula recommendation", exception);
        } finally {
            closeQuietly(connection);
        }
    }

    public Map<String, Object> findLatestByFormulaId(String formulaId) {
        String sql = "select formula_id, request_id, goal, created_at, formula_json "
                + "from formula_candidate where formula_id = ? order by id desc limit 1";
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet resultSet = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, formulaId);
            resultSet = statement.executeQuery();
            if (!resultSet.next()) {
                return null;
            }
            Map<String, Object> row = new LinkedHashMap<String, Object>();
            row.put("formula_id", resultSet.getString("formula_id"));
            row.put("request_id", resultSet.getString("request_id"));
            row.put("goal", resultSet.getString("goal"));
            row.put("stored_at", resultSet.getString("created_at"));
            row.put("formula", objectMapper.readValue(
                    resultSet.getString("formula_json"),
                    new TypeReference<Map<String, Object>>() {
                    }
            ));
            return row;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to load archived formula candidate", exception);
        } finally {
            closeQuietly(resultSet);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private void saveRequest(Connection connection, FormulaRecommendationResponse response) throws Exception {
        String sql = "insert into formula_request (request_id, goal, constraints_json) values (?, ?, '{}')";
        PreparedStatement statement = null;
        try {
            statement = connection.prepareStatement(sql);
            statement.setString(1, response.getRequestId());
            statement.setString(2, response.getGoal());
            statement.executeUpdate();
        } finally {
            closeQuietly(statement);
        }
    }

    private void saveCandidate(Connection connection, FormulaRecommendationResponse response, FormulaCandidate formula)
            throws Exception {
        String sql = "insert into formula_candidate "
                + "(formula_id, request_id, goal, status, formula_json, ingredient_ids_json, evidence_ids_json, "
                + "risk_notes_json, score_total, score_json) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        PreparedStatement statement = null;
        try {
            statement = connection.prepareStatement(sql);
            statement.setString(1, formula.getId());
            statement.setString(2, firstNonBlank(formula.getRequestId(), response.getRequestId()));
            statement.setString(3, firstNonBlank(formula.getGoal(), response.getGoal()));
            statement.setString(4, firstNonBlank(formula.getStatus(), "candidate"));
            statement.setString(5, objectMapper.writeValueAsString(formula));
            statement.setString(6, objectMapper.writeValueAsString(ingredientIds(formula)));
            statement.setString(7, objectMapper.writeValueAsString(nullToEmpty(formula.getEvidenceIds())));
            statement.setString(8, objectMapper.writeValueAsString(nullToEmpty(formula.getRiskNotes())));
            statement.setDouble(9, scoreTotal(formula));
            statement.setString(10, objectMapper.writeValueAsString(formula.getScore()));
            statement.executeUpdate();
        } finally {
            closeQuietly(statement);
        }
    }

    private List<FormulaCandidate> safeFormulas(FormulaRecommendationResponse response) {
        if (response.getFormulas() == null) {
            return new ArrayList<FormulaCandidate>();
        }
        return response.getFormulas();
    }

    private List<String> ingredientIds(FormulaCandidate formula) {
        List<String> ingredientIds = new ArrayList<String>();
        if (formula.getIngredients() == null) {
            return ingredientIds;
        }
        for (FormulaIngredient ingredient : formula.getIngredients()) {
            if (ingredient.getIngredientId() != null) {
                ingredientIds.add(ingredient.getIngredientId());
            }
        }
        return ingredientIds;
    }

    private List<String> nullToEmpty(List<String> values) {
        if (values == null) {
            return new ArrayList<String>();
        }
        return values;
    }

    private double scoreTotal(FormulaCandidate formula) {
        if (formula.getScore() == null || formula.getScore().getOverall() == null) {
            return 0.0d;
        }
        BigDecimal overall = formula.getScore().getOverall();
        return overall.doubleValue();
    }

    private String firstNonBlank(String primary, String fallback) {
        if (primary != null && primary.trim().length() > 0) {
            return primary;
        }
        return fallback;
    }

    private void rollbackQuietly(Connection connection) {
        if (connection == null) {
            return;
        }
        try {
            connection.rollback();
        } catch (SQLException ignored) {
        }
    }

    private void closeQuietly(AutoCloseable closeable) {
        if (closeable == null) {
            return;
        }
        try {
            closeable.close();
        } catch (Exception ignored) {
        }
    }
}
