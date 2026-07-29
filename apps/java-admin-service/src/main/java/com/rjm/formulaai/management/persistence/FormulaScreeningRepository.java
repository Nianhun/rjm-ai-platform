package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningRecord;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class FormulaScreeningRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public FormulaScreeningRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public ScreeningStoredResponse recordScreening(String formulaId, FormulaScreeningRequest request) {
        String sql = "insert into formula_screening "
                + "(formula_id, engineer, decision, reason, modified_ingredients_json) values (?, ?, ?, ?, ?)";
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, formulaId);
            statement.setString(2, request.getEngineer());
            statement.setString(3, request.getDecision());
            statement.setString(4, request.getReason());
            statement.setString(5, objectMapper.writeValueAsString(nullToEmpty(request.getModifiedIngredients())));
            statement.executeUpdate();
            return new ScreeningStoredResponse(true, countByFormulaId(connection, formulaId));
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to record formula screening", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public ScreeningListResponse listScreening(String formulaId) {
        String sql = "select formula_id, engineer, decision, reason, modified_ingredients_json "
                + "from formula_screening where formula_id = ? order by id asc";
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, formulaId);
            rows = statement.executeQuery();
            List<ScreeningRecord> records = new ArrayList<ScreeningRecord>();
            while (rows.next()) {
                records.add(new ScreeningRecord(
                        rows.getString("formula_id"),
                        rows.getString("engineer"),
                        rows.getString("decision"),
                        rows.getString("reason"),
                        readModifiedIngredients(rows.getString("modified_ingredients_json"))
                ));
            }
            return new ScreeningListResponse(formulaId, records);
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to list formula screenings", exception);
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
            statement = connection.prepareStatement("select count(*) from formula_screening where formula_id = ?");
            statement.setString(1, formulaId);
            rows = statement.executeQuery();
            return rows.next() ? rows.getInt(1) : 0;
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
        }
    }

    private List<FormulaIngredient> readModifiedIngredients(String json) throws Exception {
        if (json == null || json.trim().length() == 0) {
            return new ArrayList<FormulaIngredient>();
        }
        return objectMapper.readValue(json, new TypeReference<List<FormulaIngredient>>() {
        });
    }

    private List<FormulaIngredient> nullToEmpty(List<FormulaIngredient> values) {
        if (values == null) {
            return new ArrayList<FormulaIngredient>();
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
