package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ExperimentFeedbackRequest;
import com.rjm.formulaai.management.dto.FeedbackStoredResponse;
import org.junit.jupiter.api.Test;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class ExperimentFeedbackRepositoryTests {
    @Test
    void recordFeedbackPersistsExperimentFieldsAndReturnsFormulaCount() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement insertStatement = mock(PreparedStatement.class);
        PreparedStatement countStatement = mock(PreparedStatement.class);
        ResultSet countRows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("insert into experiment_feedback"))).thenReturn(insertStatement);
        when(connection.prepareStatement(contains("select count(*)"))).thenReturn(countStatement);
        when(countStatement.executeQuery()).thenReturn(countRows);
        when(countRows.next()).thenReturn(true);
        when(countRows.getInt(1)).thenReturn(2);

        ExperimentFeedbackRepository repository = new ExperimentFeedbackRepository(dataSource, new ObjectMapper());
        FeedbackStoredResponse response = repository.recordFeedback(request());

        verify(insertStatement).setString(1, "FORM-MOIST-001");
        verify(insertStatement).setString(2, "BATCH-20260728-001");
        verify(insertStatement).setString(3, "pass");
        verify(insertStatement).setString(eq(4), contains("ING-GLYCERIN"));
        verify(insertStatement).setString(eq(5), contains("hydration_after_2h"));
        verify(insertStatement).setString(eq(6), contains("sticky"));
        verify(insertStatement).setString(7, "stable enough for pilot");
        verify(insertStatement).setString(8, "engineer_a");
        verify(countStatement).setString(1, "FORM-MOIST-001");
        assertEquals(true, response.isStored());
        assertEquals(2, response.getFeedbackCount());
    }

    @Test
    void countByFormulaIdReturnsZeroWhenNoRowsExist() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("select count(*)"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(false);

        ExperimentFeedbackRepository repository = new ExperimentFeedbackRepository(dataSource, new ObjectMapper());

        assertEquals(0, repository.countByFormulaId("FORM-MOIST-404"));
        verify(statement).setString(1, "FORM-MOIST-404");
    }

    @Test
    void countPassingByFormulaIdFiltersToPassingFeedback() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("result = ?"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true);
        when(rows.getInt(1)).thenReturn(3);

        ExperimentFeedbackRepository repository = new ExperimentFeedbackRepository(dataSource, new ObjectMapper());

        assertEquals(3, repository.countPassingByFormulaId("FORM-MOIST-002"));
        verify(statement).setString(1, "FORM-MOIST-002");
        verify(statement).setString(2, "pass");
    }

    @Test
    void countPassingByIngredientIdMatchesIngredientJson() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("ingredient_ids_json like ?"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true);
        when(rows.getInt(1)).thenReturn(4);

        ExperimentFeedbackRepository repository = new ExperimentFeedbackRepository(dataSource, new ObjectMapper());

        assertEquals(4, repository.countPassingByIngredientId("ING-GLYCERIN"));
        verify(statement).setString(1, "pass");
        verify(statement).setString(2, "%\"ING-GLYCERIN\"%");
    }

    @Test
    void countPassingByIngredientPairRequiresBothIngredients() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("ingredient_ids_json like ? and ingredient_ids_json like ?")))
                .thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true);
        when(rows.getInt(1)).thenReturn(2);

        ExperimentFeedbackRepository repository = new ExperimentFeedbackRepository(dataSource, new ObjectMapper());

        assertEquals(2, repository.countPassingByIngredientPair("ING-GLYCERIN", "ING-PANTHENOL"));
        verify(statement).setString(1, "pass");
        verify(statement).setString(2, "%\"ING-GLYCERIN\"%");
        verify(statement).setString(3, "%\"ING-PANTHENOL\"%");
    }

    private ExperimentFeedbackRequest request() {
        ExperimentFeedbackRequest request = new ExperimentFeedbackRequest();
        request.setFormulaId("FORM-MOIST-001");
        request.setBatchNo("BATCH-20260728-001");
        request.setResult("pass");
        request.setIngredientIds(Arrays.asList("ING-GLYCERIN", "ING-HA"));
        Map<String, Object> metrics = new LinkedHashMap<String, Object>();
        metrics.put("hydration_after_2h", 31.5);
        request.setMetrics(metrics);
        request.setIssues(Collections.singletonList("sticky"));
        request.setEngineerConclusion("stable enough for pilot");
        request.setEngineer("engineer_a");
        return request;
    }
}
