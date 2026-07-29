package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.HealthResponse;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {
    @GetMapping("/api/health")
    public HealthResponse getHealth() {
        return new HealthResponse("ok");
    }
}
