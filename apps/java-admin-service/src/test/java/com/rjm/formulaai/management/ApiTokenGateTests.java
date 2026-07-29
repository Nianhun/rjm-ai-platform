package com.rjm.formulaai.management;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {
        "rjm.console.location=classpath:/test-console/",
        "rjm.security.api-token.enabled=true",
        "rjm.security.api-token.value=dev-secret"
})
@AutoConfigureMockMvc
class ApiTokenGateTests {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void rejectsApiRequestsWithoutTokenWhenGateEnabled() throws Exception {
        mockMvc.perform(post("/api/formulas/recommend")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-SEC\",\"goal\":\"保湿\"}"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void acceptsApiRequestsWithTokenWhenGateEnabled() throws Exception {
        mockMvc.perform(post("/api/formulas/recommend")
                        .header("X-RJM-API-Token", "dev-secret")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-SEC\",\"goal\":\"保湿\"}"))
                .andExpect(status().isOk());
    }

    @Test
    void keepsConsoleHtmlPublicWhenApiTokenGateEnabled() throws Exception {
        mockMvc.perform(get("/console/index.html"))
                .andExpect(status().isOk());
    }
}
