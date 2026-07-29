package com.rjm.formulaai.management.persistence;

import org.junit.jupiter.api.Test;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class LearnedWeightRepositoryTests {
    @Test
    void saveWeightUpdatesExistingAuditRecordBeforeInsert() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement updateStatement = mock(PreparedStatement.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("update learned_weight"))).thenReturn(updateStatement);
        when(updateStatement.executeUpdate()).thenReturn(1);

        LearnedWeightRepository repository = new LearnedWeightRepository(dataSource);
        repository.saveWeight(
                "moisturizing",
                "ingredient_pair",
                "ING-GLYCERIN+ING-PANTHENOL",
                new BigDecimal("0.12"),
                4,
                "experiment_feedback",
                "4 passing feedback records capped at 0.12");

        verify(updateStatement).setDouble(1, 0.12d);
        verify(updateStatement).setInt(2, 4);
        verify(updateStatement).setString(3, "experiment_feedback");
        verify(updateStatement).setString(4, "4 passing feedback records capped at 0.12");
        verify(updateStatement).setString(5, "moisturizing");
        verify(updateStatement).setString(6, "ingredient_pair");
        verify(updateStatement).setString(7, "ING-GLYCERIN+ING-PANTHENOL");
    }

    @Test
    void listWeightsReturnsRecordsForGoalAndTargetType() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet rows = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("from learned_weight"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(rows);
        when(rows.next()).thenReturn(true, false);
        when(rows.getString("goal")).thenReturn("moisturizing");
        when(rows.getString("target_type")).thenReturn("ingredient");
        when(rows.getString("target_key")).thenReturn("ING-GLYCERIN");
        when(rows.getBigDecimal("weight")).thenReturn(new BigDecimal("0.09"));
        when(rows.getInt("evidence_count")).thenReturn(3);
        when(rows.getString("source")).thenReturn("experiment_feedback");
        when(rows.getString("calculation_note")).thenReturn("3 passing feedback records");

        LearnedWeightRepository repository = new LearnedWeightRepository(dataSource);
        List<LearnedWeightRecord> weights = repository.listWeights("moisturizing", "ingredient");

        verify(statement).setString(1, "moisturizing");
        verify(statement).setString(2, "ingredient");
        assertEquals(1, weights.size());
        assertEquals("ING-GLYCERIN", weights.get(0).getTargetKey());
        assertEquals(new BigDecimal("0.09"), weights.get(0).getWeight());
        assertEquals(3, weights.get(0).getEvidenceCount());
    }
}
