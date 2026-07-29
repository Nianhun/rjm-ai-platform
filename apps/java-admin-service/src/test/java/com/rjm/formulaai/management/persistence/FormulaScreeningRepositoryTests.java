package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaScreeningRequest;
import com.rjm.formulaai.management.dto.ScreeningListResponse;
import com.rjm.formulaai.management.dto.ScreeningStoredResponse;
import org.junit.jupiter.api.Test;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class FormulaScreeningRepositoryTests {
    @Test
    void recordScreeningPersistsDecisionAndReturnsCount() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement insertStatement = mock(PreparedStatement.class);
        PreparedStatement countStatement = mock(PreparedStatement.class);
        ResultSet countRows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("insert into formula_screening"))).thenReturn(insertStatement);
        when(connection.prepareStatement(contains("select count(*)"))).thenReturn(countStatement);
        when(countStatement.executeQuery()).thenReturn(countRows);
        when(countRows.next()).thenReturn(true);
        when(countRows.getInt(1)).thenReturn(1);

        FormulaScreeningRepository repository = new FormulaScreeningRepository(dataSource, objectMapper());
        ScreeningStoredResponse response = repository.recordScreening("FORM-MOIST-001", request());

        verify(insertStatement).setString(1, "FORM-MOIST-001");
        verify(insertStatement).setString(2, "engineer_a");
        verify(insertStatement).setString(3, "keep");
        verify(insertStatement).setString(4, "进入小试");
        verify(insertStatement).setString(eq(5), contains("ING-GLYCERIN"));
        verify(countStatement).setString(1, "FORM-MOIST-001");
        assertEquals(true, response.isStored());
        assertEquals(1, response.getScreeningCount());
    }

    @Test
    void listScreeningReadsRowsByFormulaId() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("from formula_screening"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true, false);
        when(rows.getString("formula_id")).thenReturn("FORM-MOIST-001");
        when(rows.getString("engineer")).thenReturn("engineer_a");
        when(rows.getString("decision")).thenReturn("keep");
        when(rows.getString("reason")).thenReturn("进入小试");
        when(rows.getString("modified_ingredients_json")).thenReturn("[{\"ingredient_id\":\"ING-GLYCERIN\"}]");

        FormulaScreeningRepository repository = new FormulaScreeningRepository(dataSource, objectMapper());
        ScreeningListResponse response = repository.listScreening("FORM-MOIST-001");

        verify(statement).setString(1, "FORM-MOIST-001");
        assertEquals("FORM-MOIST-001", response.getFormulaId());
        assertEquals(1, response.getRecords().size());
        assertEquals("engineer_a", response.getRecords().get(0).getEngineer());
        assertEquals("ING-GLYCERIN", response.getRecords().get(0).getModifiedIngredients().get(0).getIngredientId());
    }

    private FormulaScreeningRequest request() {
        FormulaIngredient modified = new FormulaIngredient(
                "ING-GLYCERIN",
                "降低粘腻感",
                BigDecimal.valueOf(1.0),
                BigDecimal.valueOf(2.0));
        return new FormulaScreeningRequest("engineer_a", "keep", "进入小试", Arrays.asList(modified));
    }

    private ObjectMapper objectMapper() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.setPropertyNamingStrategy(PropertyNamingStrategy.SNAKE_CASE);
        return objectMapper;
    }
}
