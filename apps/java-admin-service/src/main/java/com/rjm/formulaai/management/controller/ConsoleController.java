package com.rjm.formulaai.management.controller;

import java.nio.file.Path;
import java.nio.file.Paths;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ConsoleController {
    private final ResourceLoader resourceLoader;

    @Value("${rjm.console.location:}")
    private String configuredConsoleLocation;

    public ConsoleController(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
    }

    @GetMapping("/")
    public String redirectToConsole() {
        return "redirect:/console/";
    }

    @GetMapping({
            "/console",
            "/console/",
            "/console/formulas",
            "/console/chat",
            "/console/elements",
            "/console/history",
            "/console/invites",
            "/console/experiments",
            "/console/learning",
            "/console/procurement",
            "/console/output",
            "/console/settings",
            "/console/formula-detail"
    })
    public ResponseEntity<Resource> serveConsoleShell() {
        return ResponseEntity.ok()
                .contentType(MediaType.TEXT_HTML)
                .cacheControl(CacheControl.noStore())
                .body(consoleIndexResource());
    }

    private Resource consoleIndexResource() {
        return resourceLoader.getResource(consoleLocation() + "index.html");
    }

    private String consoleLocation() {
        if (configuredConsoleLocation != null && configuredConsoleLocation.trim().length() > 0) {
            String trimmed = configuredConsoleLocation.trim();
            return trimmed.endsWith("/") ? trimmed : trimmed + "/";
        }
        Path serviceRoot = Paths.get("").toAbsolutePath();
        Path projectRoot = serviceRoot.getParent() == null ? serviceRoot : serviceRoot.getParent().getParent();
        Path consoleRoot = projectRoot.resolve("apps").resolve("engineer-console").normalize();
        return consoleRoot.toUri().toString() + "/";
    }
}
