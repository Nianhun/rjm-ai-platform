package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.persistence.HistoryRepository;
import java.util.LinkedHashMap;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HistoryController {
    private final HistoryRepository historyRepository;

    public HistoryController(HistoryRepository historyRepository) {
        this.historyRepository = historyRepository;
    }

    @GetMapping("/api/history/formulas")
    public Map<String, Object> formulaHistory(
            HttpServletRequest request,
            @RequestParam(defaultValue = "50") int limit) {
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("items", historyRepository.listFormulaHistory(currentEmail(request), limit));
        return result;
    }

    @GetMapping("/api/history/chats")
    public Map<String, Object> chatHistory(
            HttpServletRequest request,
            @RequestParam(defaultValue = "50") int limit) {
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("items", historyRepository.listChatHistory(currentEmail(request), limit));
        return result;
    }

    private String currentEmail(HttpServletRequest request) {
        return String.valueOf(request.getAttribute("currentUserEmail"));
    }
}
