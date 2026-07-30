package com.rjm.formulaai.management;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest(properties = {
        "rjm.ai-service.mode=mock",
        "rjm.auth.enabled=true",
        "rjm.auth.bootstrap-invite-code=TEST-BOOTSTRAP",
        "rjm.local-db.enabled=true",
        "rjm.local-db.url=jdbc:h2:mem:rjm_auth_history;DB_CLOSE_DELAY=-1",
        "rjm.local-db.schema-path=../../infrastructure/database/java-management/schema.h2.sql"
})
@AutoConfigureMockMvc
class AuthAndHistoryApiTests {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void registersWithEmailCodeAndSingleUseInviteThenRecordsHistory() throws Exception {
        String email = "engineer-" + UUID.randomUUID().toString().replace("-", "") + "@example.com";
        String code = sendCode(email);

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"weak\",\"invite_code\":\"TEST-BOOTSTRAP\",\"verification_code\":\"" + code + "\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").value("密码至少 6 位，并且必须同时包含英文大写、小写和数字"));

        String token = register(email, code, "TEST-BOOTSTRAP");

        mockMvc.perform(get("/api/knowledge/status"))
                .andExpect(status().isUnauthorized());

        mockMvc.perform(post("/api/invites")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").exists());

        mockMvc.perform(get("/api/invites")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items.length()", greaterThanOrEqualTo(1)));

        mockMvc.perform(post("/api/formulas/recommend")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"REQ-HISTORY-1\",\"goal\":\"保湿\",\"dosage_form\":\"乳液\",\"constraints\":{}}"))
                .andExpect(status().isOk());

        mockMvc.perform(post("/api/ai/chat")
                        .header("Authorization", "Bearer " + token)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"id\":\"CHAT-HISTORY-1\",\"message\":\"保湿乳液如何降低粘腻感？\",\"history\":[],\"context\":{}}"))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/history/formulas")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[0].request_id").value("REQ-HISTORY-1"));

        mockMvc.perform(get("/api/history/chats")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.items[0].message").value("保湿乳液如何降低粘腻感？"));
    }

    private String sendCode(String email) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/auth/email-code")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\"}"))
                .andExpect(status().isOk())
                .andReturn();
        JsonNode json = objectMapper.readTree(result.getResponse().getContentAsString());
        return json.get("dev_code").asText();
    }

    private String register(String email, String code, String inviteCode) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"Aa123456\",\"invite_code\":\"" + inviteCode + "\",\"verification_code\":\"" + code + "\"}"))
                .andExpect(status().isOk())
                .andReturn();
        JsonNode json = objectMapper.readTree(result.getResponse().getContentAsString());
        return json.get("token").asText();
    }
}
