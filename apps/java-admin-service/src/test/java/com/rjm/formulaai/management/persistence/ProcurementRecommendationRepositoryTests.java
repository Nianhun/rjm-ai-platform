package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rjm.formulaai.management.dto.ProcurementItem;
import com.rjm.formulaai.management.dto.ProcurementRecommendationResponse;
import com.rjm.formulaai.management.dto.RawMaterialSkuRecommendation;
import org.h2.jdbcx.JdbcDataSource;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.Statement;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.assertEquals;

class ProcurementRecommendationRepositoryTests {
    @Test
    void savesListsAndUpdatesProcurementRecommendations() throws Exception {
        ProcurementRecommendationRepository repository =
                new ProcurementRecommendationRepository(dataSource(), new ObjectMapper());
        RawMaterialSkuRecommendation sku = new RawMaterialSkuRecommendation(
                "SKU-GLYCERIN-001",
                "SUP-001",
                "cosmetic grade glycerin",
                Collections.<String, Object>singletonMap("currency", "CNY"),
                new BigDecimal("25"),
                7,
                Collections.singletonList("coa.pdf"),
                "available",
                new BigDecimal("0.92"),
                new BigDecimal("0.88"));
        ProcurementRecommendationResponse response = new ProcurementRecommendationResponse(
                "FORM-MOIST-001",
                Collections.singletonList(new ProcurementItem(
                        "ING-GLYCERIN",
                        "matched",
                        Collections.singletonList(sku))));

        repository.saveRecommendation(response);
        ProcurementRecommendationResponse stored = repository.listRecommendations("FORM-MOIST-001");

        assertEquals("FORM-MOIST-001", stored.getFormulaId());
        assertEquals("ING-GLYCERIN", stored.getItems().get(0).getIngredientId());
        assertEquals("matched", stored.getItems().get(0).getStatus());
        assertEquals("SKU-GLYCERIN-001", stored.getItems().get(0).getRecommendedSkus().get(0).getSkuId());

        ProcurementStatusUpdateResponse updated = repository.updateStatus(
                "FORM-MOIST-001", "ING-GLYCERIN", "sample_requested");

        assertEquals(true, updated.isUpdated());
        assertEquals("sample_requested", repository.listRecommendations("FORM-MOIST-001").getItems().get(0).getStatus());
    }

    private JdbcDataSource dataSource() throws Exception {
        JdbcDataSource dataSource = new JdbcDataSource();
        dataSource.setURL("jdbc:h2:mem:rjm_procurement_test;DB_CLOSE_DELAY=-1");
        dataSource.setUser("sa");
        dataSource.setPassword("");
        String schema = new String(
                Files.readAllBytes(Paths.get("..", "..", "infrastructure", "database", "java-management", "schema.h2.sql").toAbsolutePath()),
                StandardCharsets.UTF_8);
        Connection connection = dataSource.getConnection();
        try {
            Statement statement = connection.createStatement();
            try {
                statement.execute(schema);
            } finally {
                statement.close();
            }
        } finally {
            connection.close();
        }
        return dataSource;
    }
}
