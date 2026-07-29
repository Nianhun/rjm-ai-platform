package com.rjm.formulaai.management.config;

import java.nio.file.Path;
import java.nio.file.Paths;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.CacheControl;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConsoleConfig implements WebMvcConfigurer {
    @Value("${rjm.console.location:}")
    private String configuredConsoleLocation;

    @Value("${rjm.security.api-token.enabled:false}")
    private boolean apiTokenEnabled;

    @Value("${rjm.security.api-token.value:}")
    private String apiTokenValue;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String consoleLocation = engineerConsoleLocation();
        registry.addResourceHandler("/console/**")
                .addResourceLocations(consoleLocation)
                .setCacheControl(CacheControl.noStore());
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("http://localhost:8080", "http://127.0.0.1:8080", "null")
                .allowedMethods("GET", "POST", "PATCH", "OPTIONS")
                .allowedHeaders("*")
                .maxAge(3600);
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new HandlerInterceptor() {
            @Override
            public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
                    throws Exception {
                if (!apiTokenEnabled || "OPTIONS".equalsIgnoreCase(request.getMethod())) {
                    return true;
                }
                String configuredToken = apiTokenValue == null ? "" : apiTokenValue.trim();
                String requestToken = request.getHeader("X-RJM-API-Token");
                if (configuredToken.length() > 0 && configuredToken.equals(requestToken)) {
                    return true;
                }
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or invalid X-RJM-API-Token");
                return false;
            }
        }).addPathPatterns("/api/**");
    }

    private String engineerConsoleLocation() {
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
