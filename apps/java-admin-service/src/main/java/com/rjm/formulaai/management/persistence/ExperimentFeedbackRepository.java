package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ExperimentFeedbackRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public ExperimentFeedbackRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public FeedbackStoredResponse recordFeedback(ExperimentFeedbackRequest request) {
        String sql = "insert into experiment_feedback "
                + "(formula_id, batch_no, result, ingredient_ids_json, metrics_json, issues_json, "
                + "engineer_conclusion, engineer) values (?, ?, ?, ?, ?, ?, ?, ?)";
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, request.getFormulaId());
            statement.setString(2, request.getBatchNo());
            statement.setString(3, request.getResult());
            statement.setString(4, objectMapper.writeValueAsString(nullToEmpty(request.getIngredientIds())));
            statement.setString(5, objectMapper.writeValueAsString(nullToEmpty(request.getMetrics())));
            statement.setString(6, objectMapper.writeValueAsString(nullToEmpty(request.getIssues())));
            statement.setString(7, request.getEngineerConclusion());
            statement.setString(8, request.getEngineer());
            statement.executeUpdate();
            return new FeedbackStoredResponse(true, countByFormulaId(connection, request.getFormulaId()));
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to record experiment feedback", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public int countByFormulaId(String formulaId) {
        Connection connection = null;
        try {
            connection = dataSource.getConnection();
            return countByFormulaId(connection, formulaId);
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to count experiment feedback", exception);
        } finally {
            closeQuietly(connection);
        }
    }

    public int countPassingByFormulaId(String formulaId) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(
                    "select count(*) from experiment_feedback where formula_id = ? and result = ?");
            statement.setString(1, formulaId);
            statement.setString(2, "pass");
            rows = statement.executeQuery();
            return rows.next() ? rows.getInt(1) : 0;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to count passing experiment feedback", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public int countPassingByIngredientId(String ingredientId) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(
                    "select count(*) from experiment_feedback where result = ? and ingredient_ids_json like ?");
            statement.setString(1, "pass");
            statement.setString(2, "%\"" + ingredientId + "\"%");
            rows = statement.executeQuery();
            return rows.next() ? rows.getInt(1) : 0;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to count passing experiment feedback by ingredient", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public int countPassingByIngredientPair(String firstIngredientId, String secondIngredientId) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement("select count(*) from experiment_feedback "
                    + "where result = ? and ingredient_ids_json like ? and ingredient_ids_json like ?");
            statement.setString(1, "pass");
            statement.setString(2, "%\"" + firstIngredientId + "\"%");
            statement.setString(3, "%\"" + secondIngredientId + "\"%");
            rows = statement.executeQuery();
            return rows.next() ? rows.getInt(1) : 0;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to count passing experiment feedback by ingredient pair", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private int countByFormulaId(Connection connection, String formulaId) throws Exception {
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            statement = connection.prepareStatement("select count(*) from experiment_feedback where formula_id = ?");
            statement.setString(1, formulaId);
            rows = statement.executeQuery();
            return rows.next() ? rows.getInt(1) : 0;
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
        }
    }

    private List<String> nullToEmpty(List<String> values) {
        if (values == null) {
            return new ArrayList<String>();
        }
        return values;
    }

    private Map<String, Object> nullToEmpty(Map<String, Object> values) {
        if (values == null) {
            return new LinkedHashMap<String, Object>();
        }
        return values;
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
