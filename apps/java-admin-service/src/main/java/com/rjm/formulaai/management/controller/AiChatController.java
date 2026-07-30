package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.dto.AiChatRequest;
import com.rjm.formulaai.management.dto.AiChatResponse;
import com.rjm.formulaai.management.persistence.HistoryRepository;
import com.rjm.formulaai.management.service.FormulaAiManagementService;
import javax.servlet.http.HttpServletRequest;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AiChatController {
    private final FormulaAiManagementService service;

    @Autowired(required = false)
    private HistoryRepository historyRepository;

    public AiChatController(FormulaAiManagementService service) {
        this.service = service;
    }

    @PostMapping("/api/ai/chat")
    public AiChatResponse chat(@Valid @RequestBody AiChatRequest request, HttpServletRequest httpRequest) {
        AiChatResponse response = service.chat(request);
        if (historyRepository != null) {
            historyRepository.recordChat(currentEmail(httpRequest), request, response);
        }
        return response;
    }

    private String currentEmail(HttpServletRequest request) {
        Object value = request.getAttribute("currentUserEmail");
        return value == null ? "" : String.valueOf(value);
    }
}
