package com.rjm.formulaai.management;

import org.h2.jdbcx.JdbcDataSource;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import javax.sql.DataSource;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.hamcrest.Matchers.hasItem;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(properties = {"rjm.ai-service.mode=db", "rjm.auth.enabled=false"})
@AutoConfigureMockMvc
class DbModeH2IntegrationTests {
    @javax.annotation.Resource
    private MockMvc mockMvc;

    @javax.annotation.Resource
    private DataSource dataSource;

    @Test
    void dbModePersistsRecommendationAndReadsArchiveFromRealH2Database() throws Exception {
        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-H2-001\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formulas[0].id").value("FORM-MOIST-001"));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.request_id").value("REQ-H2-001"))
                .andExpect(jsonPath("$.formula.id").value("FORM-MOIST-001"));

        mockMvc.perform(post("/api/formulas/FORM-MOIST-001/screenings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"engineer\":\"engineer_a\",\"decision\":\"keep\",\"reason\":\"进入小试\",\"modified_ingredients\":[]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true))
                .andExpect(jsonPath("$.screening_count").value(1));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001/screenings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.records[0].engineer").value("engineer_a"))
                .andExpect(jsonPath("$.records[0].decision").value("keep"));

        mockMvc.perform(post("/api/experiments/batches")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"batch_no\":\"BATCH-H2-PLANNED\",\"formula_id\":\"FORM-MOIST-001\",\"stage\":\"lab_trial\",\"owner\":\"engineer_a\",\"metrics\":{\"target_hydration_after_2h\":30},\"issues\":[],\"conclusion\":\"scheduled\",\"status\":\"running\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.batch_no").value("BATCH-H2-PLANNED"))
                .andExpect(jsonPath("$.status").value("running"));

        mockMvc.perform(get("/api/experiments/batches")
                        .param("formula_id", "FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.batches[0].batch_no").value("BATCH-H2-PLANNED"));

        assertEquals(0, feedbackRows("FORM-MOIST-001"));

        mockMvc.perform(post("/api/experiments/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula_id\":\"FORM-MOIST-001\",\"batch_no\":\"BATCH-H2-001\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-GLYCERIN\"],\"metrics\":{\"hydration_after_2h\":31.5},\"issues\":[\"sticky\"],\"engineer_conclusion\":\"stable enough for pilot\",\"engineer\":\"engineer_a\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true))
                .andExpect(jsonPath("$.feedback_count").value(1));

        mockMvc.perform(post("/api/reports/feedback-impact")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-H2-REPORT\",\"goal\":\"moisturizing\",\"dosage_form\":\"lotion\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-H2-REPORT"))
                .andExpect(jsonPath("$.feedback_count").value(1));

        for (int index = 1; index <= 4; index++) {
            mockMvc.perform(post("/api/experiments/feedback")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"formula_id\":\"FORM-EXTERNAL-GLYCERIN\",\"batch_no\":\"BATCH-H2-ING-" + index + "\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-GLYCERIN\"]}"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.stored").value(true));
        }

        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-H2-LEARNED\",\"goal\":\"moisturizing\",\"dosage_form\":\"lotion\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formulas[0].id").value("FORM-MOIST-002"))
                .andExpect(jsonPath("$.formulas[0].score.overall").value(0.934));

        for (int index = 1; index <= 4; index++) {
            mockMvc.perform(post("/api/experiments/feedback")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"formula_id\":\"FORM-EXTERNAL-PAIR\",\"batch_no\":\"BATCH-H2-PAIR-" + index + "\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-GLYCERIN\",\"ING-PANTHENOL\"]}"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.stored").value(true));
        }

        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-H2-PAIR-LEARNED\",\"goal\":\"moisturizing\",\"dosage_form\":\"lotion\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formulas[0].id").value("FORM-MOIST-002"));

        assertEquals(0.12d, learnedWeight("moisturizing", "ingredient", "ING-GLYCERIN"), 0.001d);
        assertEquals(0.12d, learnedWeight(
                "moisturizing", "ingredient_pair", "ING-GLYCERIN+ING-PANTHENOL"), 0.001d);

        mockMvc.perform(get("/api/learning/weights")
                        .param("goal", "moisturizing")
                        .param("target_type", "ingredient_pair"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.weights[0].target_key").value("ING-GLYCERIN+ING-PANTHENOL"))
                .andExpect(jsonPath("$.weights[0].weight").value(0.12));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-002/explanation")
                        .param("goal", "moisturizing"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-002"))
                .andExpect(jsonPath("$.influences[*].target_key")
                        .value(hasItem("ING-GLYCERIN+ING-PANTHENOL")));

        mockMvc.perform(post("/api/procurement/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula\":{\"id\":\"FORM-MOIST-002\",\"ingredients\":[{\"ingredient_id\":\"ING-GLYCERIN\"}],\"score\":{\"overall\":0.9},\"status\":\"ai_recommended\"}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-002"))
                .andExpect(jsonPath("$.items[0].ingredient_id").value("ING-GLYCERIN"));

        mockMvc.perform(get("/api/procurement/recommendations/FORM-MOIST-002"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-002"))
                .andExpect(jsonPath("$.items[0].ingredient_id").value("ING-GLYCERIN"))
                .andExpect(jsonPath("$.items[0].status").value("matched"));

        mockMvc.perform(patch("/api/procurement/recommendations/FORM-MOIST-002/ING-GLYCERIN/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"sample_requested\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.updated").value(true))
                .andExpect(jsonPath("$.status").value("sample_requested"));

        mockMvc.perform(get("/api/procurement/recommendations/FORM-MOIST-002"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[0].status").value("sample_requested"));
    }

    private double learnedWeight(String goal, String targetType, String targetKey) throws Exception {
        Connection connection = dataSource.getConnection();
        try {
            PreparedStatement statement = connection.prepareStatement(
                    "select weight from learned_weight where goal = ? and target_type = ? and target_key = ?");
            try {
                statement.setString(1, goal);
                statement.setString(2, targetType);
                statement.setString(3, targetKey);
                ResultSet rows = statement.executeQuery();
                try {
                    return rows.next() ? rows.getDouble(1) : 0.0d;
                } finally {
                    rows.close();
                }
            } finally {
                statement.close();
            }
        } finally {
            connection.close();
        }
    }

    private int feedbackRows(String formulaId) throws Exception {
        Connection connection = dataSource.getConnection();
        try {
            PreparedStatement statement = connection.prepareStatement(
                    "select count(*) from experiment_feedback where formula_id = ?");
            try {
                statement.setString(1, formulaId);
                ResultSet rows = statement.executeQuery();
                try {
                    return rows.next() ? rows.getInt(1) : 0;
                } finally {
                    rows.close();
                }
            } finally {
                statement.close();
            }
        } finally {
            connection.close();
        }
    }

    @TestConfiguration
    static class H2Config {
        @Bean
        public DataSource dataSource() throws Exception {
            JdbcDataSource dataSource = new JdbcDataSource();
            dataSource.setURL("jdbc:h2:mem:rjm_formula_ai;DB_CLOSE_DELAY=-1");
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
}
