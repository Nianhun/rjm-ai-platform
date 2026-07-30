package com.rjm.formulaai.management;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.options;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {"rjm.console.location=classpath:/test-console/", "rjm.auth.enabled=false"})
@AutoConfigureMockMvc
class ManagementConsoleWebTests {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void rootRedirectsToEngineerConsole() throws Exception {
        mockMvc.perform(get("/"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/console/"));
    }

    @Test
    void servesEngineerConsoleStaticHtml() throws Exception {
        mockMvc.perform(get("/console/index.html"))
                .andExpect(status().isOk())
                .andExpect(header().string(HttpHeaders.CONTENT_TYPE, containsString("text/html")))
                .andExpect(header().string(HttpHeaders.CACHE_CONTROL, containsString("no-store")))
                .andExpect(content().string(containsString("operationStatus")))
                .andExpect(content().string(containsString("selectedFormulaSummary")));
    }

    @Test
    void servesEngineerConsoleShellForDedicatedPageRoutes() throws Exception {
        for (String route : new String[] {"/console/", "/console/formulas", "/console/chat", "/console/history", "/console/settings"}) {
            mockMvc.perform(get(route))
                    .andExpect(status().isOk())
                    .andExpect(header().string(HttpHeaders.CONTENT_TYPE, containsString("text/html")))
                    .andExpect(content().string(containsString("operationStatus")))
                    .andExpect(content().string(containsString("selectedFormulaSummary")));
        }
    }

    @Test
    void allowsLocalStaticConsoleCorsPreflightForApi() throws Exception {
        mockMvc.perform(options("/api/formulas/recommend")
                        .header(HttpHeaders.ORIGIN, "http://localhost:8080")
                        .header(HttpHeaders.ACCESS_CONTROL_REQUEST_METHOD, "POST"))
                .andExpect(status().isOk())
                .andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_ORIGIN, "http://localhost:8080"))
                .andExpect(header().string(HttpHeaders.ACCESS_CONTROL_ALLOW_METHODS, containsString("POST")));
    }
}
