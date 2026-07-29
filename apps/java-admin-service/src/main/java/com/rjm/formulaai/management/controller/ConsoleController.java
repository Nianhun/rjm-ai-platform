package com.rjm.formulaai.management.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ConsoleController {
    @GetMapping("/")
    public String redirectToConsole() {
        return "redirect:/console/index.html";
    }
}
