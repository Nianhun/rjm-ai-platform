package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.persistence.AuthRepository;
import java.util.LinkedHashMap;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class InviteController {
    private final AuthRepository authRepository;

    public InviteController(AuthRepository authRepository) {
        this.authRepository = authRepository;
    }

    @PostMapping("/api/invites")
    public Map<String, Object> createInvite(HttpServletRequest request) {
        return authRepository.createInvite(currentEmail(request));
    }

    @GetMapping("/api/invites")
    public Map<String, Object> listInvites(HttpServletRequest request) {
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("items", authRepository.listInvites(currentEmail(request)));
        return result;
    }

    private String currentEmail(HttpServletRequest request) {
        return String.valueOf(request.getAttribute("currentUserEmail"));
    }
}
