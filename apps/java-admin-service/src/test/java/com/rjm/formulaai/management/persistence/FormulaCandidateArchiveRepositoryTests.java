package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.FormulaCandidate;
import com.rjm.formulaai.management.dto.FormulaIngredient;
import com.rjm.formulaai.management.dto.FormulaRecommendationResponse;
import com.rjm.formulaai.management.dto.FormulaScore;
import org.junit.jupiter.api.Test;

import javax.sql.DataSource;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Arrays;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class FormulaCandidateArchiveRepositoryTests {
    @Test
    void saveRecommendationPersistsRequestAndCandidateSnapshots() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement requestStatement = mock(PreparedStatement.class);
        PreparedStatement candidateStatement = mock(PreparedStatement.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("insert into formula_request"))).thenReturn(requestStatement);
        when(connection.prepareStatement(contains("insert into formula_candidate"))).thenReturn(candidateStatement);

        FormulaCandidateArchiveRepository repository =
                new FormulaCandidateArchiveRepository(dataSource, new ObjectMapper());
        repository.saveRecommendation(response());

        verify(requestStatement).setString(1, "REQ-JAVA-DB-001");
        verify(requestStatement).setString(2, "保湿");
        verify(candidateStatement).setString(1, "FORM-MOIST-001");
        verify(candidateStatement).setString(2, "REQ-JAVA-DB-001");
        verify(candidateStatement).setString(3, "保湿");
        verify(candidateStatement).setString(4, "candidate");
        verify(candidateStatement).setString(eq(5), contains("\"id\":\"FORM-MOIST-001\""));
        verify(candidateStatement).setString(eq(6), contains("ING-GLYCERIN"));
        verify(candidateStatement).setString(eq(7), contains("YUXI-ING-GLYCERIN"));
        verify(candidateStatement).setDouble(9, 0.91d);
        verify(requestStatement).executeUpdate();
        verify(candidateStatement).executeUpdate();
        verify(connection).commit();
    }

    @Test
    void findLatestByFormulaIdReturnsArchivedSnapshot() throws Exception {
        DataSource dataSource = mock(DataSource.class);
        Connection connection = mock(Connection.class);
        PreparedStatement statement = mock(PreparedStatement.class);
        ResultSet resultSet = mock(ResultSet.class);
        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.prepareStatement(contains("from formula_candidate"))).thenReturn(statement);
        when(statement.executeQuery()).thenReturn(resultSet);
        when(resultSet.next()).thenReturn(true);
        when(resultSet.getString("formula_id")).thenReturn("FORM-MOIST-001");
        when(resultSet.getString("request_id")).thenReturn("REQ-JAVA-DB-001");
        when(resultSet.getString("goal")).thenReturn("保湿");
        when(resultSet.getString("created_at")).thenReturn("2026-07-28T12:00:00Z");
        when(resultSet.getString("formula_json")).thenReturn("{\"id\":\"FORM-MOIST-001\",\"status\":\"candidate\"}");

        FormulaCandidateArchiveRepository repository =
                new FormulaCandidateArchiveRepository(dataSource, new ObjectMapper());
        Map<String, Object> archived = repository.findLatestByFormulaId("FORM-MOIST-001");

        verify(statement).setString(1, "FORM-MOIST-001");
        assertEquals("FORM-MOIST-001", archived.get("formula_id"));
        assertEquals("REQ-JAVA-DB-001", archived.get("request_id"));
        assertEquals("保湿", archived.get("goal"));
        assertEquals("FORM-MOIST-001", ((Map) archived.get("formula")).get("id"));
    }

    private FormulaRecommendationResponse response() {
        FormulaIngredient ingredient = new FormulaIngredient();
        ingredient.setIngredientId("ING-GLYCERIN");
        ingredient.setRole("基础保湿剂");
        FormulaScore score = new FormulaScore();
        score.setOverall(new BigDecimal("0.91"));
        FormulaCandidate candidate = new FormulaCandidate(
                "FORM-MOIST-001",
                "REQ-JAVA-DB-001",
                "保湿",
                Arrays.asList(ingredient),
                "适合进入小试",
                Arrays.asList("注意粘腻感"),
                Arrays.asList("YUXI-ING-GLYCERIN"),
                score,
                "candidate"
        );
        return new FormulaRecommendationResponse("REQ-JAVA-DB-001", "保湿", Arrays.asList(candidate));
    }
}
