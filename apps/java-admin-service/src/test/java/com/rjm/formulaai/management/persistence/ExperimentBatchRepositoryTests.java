package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ExperimentBatchRequest;
import com.rjm.formulaai.management.dto.ExperimentBatchResponse;
import org.junit.jupiter.api.Test;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class ExperimentBatchRepositoryTests {
    @Test
    void createBatchPersistsBatchFieldsAndReturnsStoredRecord() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement insertStatement = mock(PreparedStatement.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("insert into experiment_batch"))).thenReturn(insertStatement);

        ExperimentBatchRepository repository = new ExperimentBatchRepository(dataSource, new ObjectMapper());
        ExperimentBatchResponse response = repository.createBatch(request());

        verify(insertStatement).setString(1, "BATCH-MOIST-007");
        verify(insertStatement).setString(2, "FORM-MOIST-002");
        verify(insertStatement).setString(3, "lab_trial");
        verify(insertStatement).setString(4, "engineer_a");
        verify(insertStatement).setString(eq(5), contains("hydration_after_2h"));
        verify(insertStatement).setString(eq(6), contains("sticky"));
        verify(insertStatement).setString(7, "ready for 48h stability observation");
        verify(insertStatement).setString(8, "running");
        assertEquals("BATCH-MOIST-007", response.getBatchNo());
        assertEquals("FORM-MOIST-002", response.getFormulaId());
        assertEquals("running", response.getStatus());
    }

    @Test
    void listBatchesReturnsFormulaBatchesNewestFirst() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("from experiment_batch"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true, false);
        when(rows.getString("batch_no")).thenReturn("BATCH-MOIST-007");
        when(rows.getString("formula_id")).thenReturn("FORM-MOIST-002");
        when(rows.getString("stage")).thenReturn("lab_trial");
        when(rows.getString("owner")).thenReturn("engineer_a");
        when(rows.getString("metrics_json")).thenReturn("{\"hydration_after_2h\":31.5}");
        when(rows.getString("issues_json")).thenReturn("[\"sticky\"]");
        when(rows.getString("conclusion")).thenReturn("ready for 48h stability observation");
        when(rows.getString("status")).thenReturn("running");
        when(rows.getString("created_at")).thenReturn("2026-07-28 14:00:00");

        ExperimentBatchRepository repository = new ExperimentBatchRepository(dataSource, new ObjectMapper());
        List<ExperimentBatchResponse> batches = repository.listBatchesByFormula("FORM-MOIST-002");

        verify(statement).setString(1, "FORM-MOIST-002");
        assertEquals(1, batches.size());
        assertEquals("BATCH-MOIST-007", batches.get(0).getBatchNo());
        assertEquals(31.5d, ((Number) batches.get(0).getMetrics().get("hydration_after_2h")).doubleValue(), 0.001d);
        assertEquals(Collections.singletonList("sticky"), batches.get(0).getIssues());
    }

    private ExperimentBatchRequest request() {
        ExperimentBatchRequest request = new ExperimentBatchRequest();
        request.setBatchNo("BATCH-MOIST-007");
        request.setFormulaId("FORM-MOIST-002");
        request.setStage("lab_trial");
        request.setOwner("engineer_a");
        Map<String, Object> metrics = new LinkedHashMap<String, Object>();
        metrics.put("hydration_after_2h", 31.5);
        request.setMetrics(metrics);
        request.setIssues(Collections.singletonList("sticky"));
        request.setConclusion("ready for 48h stability observation");
        request.setStatus("running");
        return request;
    }
}
