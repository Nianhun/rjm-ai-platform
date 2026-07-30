package com.rjm.formulaai.management;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(properties = {"rjm.ai-service.mode=mock", "rjm.auth.enabled=false"})
class ManagementApplicationTests {
    @Test
    void contextLoads() {
    }
}
