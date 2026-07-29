package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ExperimentBatchRequest;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ExperimentBatchRepository {
    private final DataSource dataSource;
    private final ObjectMapper objectMapper;

    public ExperimentBatchRepository(DataSource dataSource, ObjectMapper objectMapper) {
        this.dataSource = dataSource;
        this.objectMapper = objectMapper;
    }

    public ExperimentBatchResponse createBatch(ExperimentBatchRequest request) {
        String sql = "insert into experiment_batch "
                + "(batch_no, formula_id, stage, owner, metrics_json, issues_json, conclusion, status) "
                + "values (?, ?, ?, ?, ?, ?, ?, ?)";
        Connection connection = null;
        PreparedStatement statement = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, request.getBatchNo());
            statement.setString(2, request.getFormulaId());
            statement.setString(3, request.getStage());
            statement.setString(4, request.getOwner());
            statement.setString(5, objectMapper.writeValueAsString(nullToEmpty(request.getMetrics())));
            statement.setString(6, objectMapper.writeValueAsString(nullToEmpty(request.getIssues())));
            statement.setString(7, request.getConclusion());
            statement.setString(8, statusOrPlanned(request.getStatus()));
            statement.executeUpdate();
            return new ExperimentBatchResponse(
                    request.getBatchNo(),
                    request.getFormulaId(),
                    request.getStage(),
                    request.getOwner(),
                    nullToEmpty(request.getMetrics()),
                    nullToEmpty(request.getIssues()),
                    request.getConclusion(),
                    statusOrPlanned(request.getStatus()),
                    null);
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to create experiment batch", exception);
        } finally {
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    public List<ExperimentBatchResponse> listBatchesByFormula(String formulaId) {
        String sql = "select batch_no, formula_id, stage, owner, metrics_json, issues_json, conclusion, status, created_at "
                + "from experiment_batch where formula_id = ? order by created_at desc, id desc";
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet rows = null;
        try {
            connection = dataSource.getConnection();
            statement = connection.prepareStatement(sql);
            statement.setString(1, formulaId);
            rows = statement.executeQuery();
            List<ExperimentBatchResponse> batches = new ArrayList<ExperimentBatchResponse>();
            while (rows.next()) {
                batches.add(new ExperimentBatchResponse(
                        rows.getString("batch_no"),
                        rows.getString("formula_id"),
                        rows.getString("stage"),
                        rows.getString("owner"),
                        readMap(rows.getString("metrics_json")),
                        readList(rows.getString("issues_json")),
                        rows.getString("conclusion"),
                        rows.getString("status"),
                        rows.getString("created_at")));
            }
            return batches;
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to list experiment batches", exception);
        } finally {
            closeQuietly(rows);
            closeQuietly(statement);
            closeQuietly(connection);
        }
    }

    private Map<String, Object> readMap(String value) throws Exception {
        if (value == null || value.length() == 0) {
            return new LinkedHashMap<String, Object>();
        }
        return objectMapper.readValue(value, new TypeReference<Map<String, Object>>() {
        });
    }

    private List<String> readList(String value) throws Exception {
        if (value == null || value.length() == 0) {
            return new ArrayList<String>();
        }
        return objectMapper.readValue(value, new TypeReference<List<String>>() {
        });
    }

    private Map<String, Object> nullToEmpty(Map<String, Object> values) {
        if (values == null) {
            return new LinkedHashMap<String, Object>();
        }
        return values;
    }

    private List<String> nullToEmpty(List<String> values) {
        if (values == null) {
            return new ArrayList<String>();
        }
        return values;
    }

    private String statusOrPlanned(String value) {
        return value == null || value.length() == 0 ? "planned" : value;
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
