package com.rjm.formulaai.management.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Collections;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.json.MappingJackson2HttpMessageConverter;
import org.springframework.web.client.RestTemplate;

@Configuration
@EnableConfigurationProperties(PythonFormulaAiProperties.class)
public class PythonFormulaAiClientConfig {
    @Bean
    public RestTemplate pythonFormulaAiRestTemplate(ObjectMapper objectMapper) {
        return new RestTemplate(Collections.singletonList(new MappingJackson2HttpMessageConverter(objectMapper)));
    }

    @Bean
    public PythonFormulaAiClient pythonFormulaAiClient(
            RestTemplate pythonFormulaAiRestTemplate,
            PythonFormulaAiProperties properties) {
        return new PythonFormulaAiClient(pythonFormulaAiRestTemplate, properties.getBaseUrl());
    }
}
