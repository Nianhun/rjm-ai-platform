package com.rjm.formulaai.management;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.jupiter.api.Assumptions.assumeTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {
        "rjm.ai-service.mode=python",
        "rjm.python-ai.base-url=${rjm.integration.python-base-url:http://127.0.0.1:8787}"
})
@AutoConfigureMockMvc
class JavaPythonIntegrationSmokeTests {
    @Autowired
    private MockMvc mockMvc;

    @BeforeAll
    static void enabledOnlyWhenRequested() {
        assumeTrue("true".equals(System.getProperty("rjm.integration.enabled")));
    }

    @Test
    void javaControllersCallRunningPythonAiService() throws Exception {
        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-JAVA-PY-001\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.request_id").value("REQ-JAVA-PY-001"))
                .andExpect(jsonPath("$.formulas", hasSize(greaterThanOrEqualTo(1))));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.formula_id").value("FORM-MOIST-001"))
                .andExpect(jsonPath("$.request_id").value("REQ-JAVA-PY-001"));

        mockMvc.perform(get("/api/knowledge/status"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ingredient_count").value(greaterThanOrEqualTo(1)))
                .andExpect(jsonPath("$.relation_count").value(greaterThanOrEqualTo(1)));

        mockMvc.perform(post("/api/formulas/FORM-MOIST-001/screenings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"engineer\":\"integration_engineer\",\"decision\":\"keep\",\"reason\":\"进入小试\",\"modified_ingredients\":[]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true));

        mockMvc.perform(get("/api/formulas/FORM-MOIST-001/screenings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.records", hasSize(greaterThanOrEqualTo(1))));

        mockMvc.perform(post("/api/experiments/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"formula_id\":\"FORM-MOIST-001\",\"batch_no\":\"BATCH-JAVA-PY-001\",\"result\":\"pass\",\"ingredient_ids\":[\"ING-BETAINE\",\"ING-PANTHENOL\"],\"metrics\":{\"stability\":\"pass\"},\"issues\":[],\"engineer\":\"lab_engineer\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.stored").value(true));

        mockMvc.perform(post("/api/reports/feedback-impact")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-JAVA-PY-REPORT\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.feedback_count").value(greaterThanOrEqualTo(1)));
        if ("true".equals(System.getProperty("rjm.integration.expect-yuxi"))) {
            mockMvc.perform(post("/api/formulas/recommend")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"id\":\"REQ-JAVA-PY-YUXI\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.request_id").value("REQ-JAVA-PY-YUXI"))
                    .andExpect(jsonPath("$.formulas", hasSize(greaterThanOrEqualTo(1))))
                    .andExpect(jsonPath("$.formulas[0].evidence_ids[0]").value(startsWith("YUXI-")));

            mockMvc.perform(get("/api/knowledge/status"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.source_paths.ingredients_path").value(org.hamcrest.Matchers.containsString("ingredients.yuxi.json")))
                    .andExpect(jsonPath("$.source_paths.evidence_path").value(org.hamcrest.Matchers.containsString("evidence.yuxi.json")))
                    .andExpect(jsonPath("$.evidence_count").value(greaterThanOrEqualTo(1)))
                    .andExpect(jsonPath("$.evidence_prefix_counts.YUXI").value(greaterThanOrEqualTo(1)));

            mockMvc.perform(get("/api/evidence/YUXI-ING-GLYCERIN"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.id").value("YUXI-ING-GLYCERIN"))
                    .andExpect(jsonPath("$.source_type").value("ingredient_profile"))
                    .andExpect(jsonPath("$.source_url").value(org.hamcrest.Matchers.containsString("glycerin")));
        }
    }
}
