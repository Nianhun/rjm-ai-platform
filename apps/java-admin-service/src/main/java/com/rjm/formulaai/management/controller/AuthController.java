package com.rjm.formulaai.management.controller;

import com.rjm.formulaai.management.persistence.AuthRepository;
import java.util.LinkedHashMap;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private final AuthRepository authRepository;

    public AuthController(AuthRepository authRepository) {
        this.authRepository = authRepository;
    }

    @PostMapping("/email-code")
    public Map<String, Object> sendEmailCode(@RequestBody Map<String, String> body) {
        return authRepository.sendEmailCode(body.get("email"));
    }

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody Map<String, String> body) {
        return authRepository.register(
                body.get("email"),
                body.get("password"),
                body.get("invite_code"),
                body.get("verification_code"));
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody Map<String, String> body) {
        return authRepository.login(body.get("email"), body.get("password"));
    }

    @GetMapping("/me")
    public Map<String, Object> me(HttpServletRequest request) {
        return authRepository.me(bearerToken(request));
    }

    @PostMapping("/logout")
    public Map<String, Object> logout(HttpServletRequest request) {
        authRepository.logout(bearerToken(request));
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("logged_out", true);
        return result;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, String>> badRequest(IllegalArgumentException exception) {
        Map<String, String> result = new LinkedHashMap<String, String>();
        result.put("error", exception.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(result);
    }

    private String bearerToken(HttpServletRequest request) {
        String authorization = request.getHeader("Authorization");
        if (authorization != null && authorization.startsWith("Bearer ")) {
            return authorization.substring("Bearer ".length()).trim();
        }
        return "";
    }
}
