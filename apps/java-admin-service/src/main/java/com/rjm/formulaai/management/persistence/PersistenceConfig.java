package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
@ConditionalOnProperty(prefix = "rjm.ai-service", name = "mode", havingValue = "db")
public class PersistenceConfig {
    @Bean
    public FormulaCandidateArchiveRepository formulaCandidateArchiveRepository(
            DataSource dataSource,
            ObjectMapper objectMapper) {
        return new FormulaCandidateArchiveRepository(dataSource, objectMapper);
    }

    @Bean
    public FormulaScreeningRepository formulaScreeningRepository(
            DataSource dataSource,
            ObjectMapper objectMapper) {
        return new FormulaScreeningRepository(dataSource, objectMapper);
    }

    @Bean
    public ExperimentFeedbackRepository experimentFeedbackRepository(
            DataSource dataSource,
            ObjectMapper objectMapper) {
        return new ExperimentFeedbackRepository(dataSource, objectMapper);
    }

    @Bean
    public ExperimentBatchRepository experimentBatchRepository(
            DataSource dataSource,
            ObjectMapper objectMapper) {
        return new ExperimentBatchRepository(dataSource, objectMapper);
    }

    @Bean
    public LearnedWeightRepository learnedWeightRepository(DataSource dataSource) {
        return new LearnedWeightRepository(dataSource);
    }

    @Bean
    public ProcurementRecommendationRepository procurementRecommendationRepository(
            DataSource dataSource,
            ObjectMapper objectMapper) {
        return new ProcurementRecommendationRepository(dataSource, objectMapper);
    }
}
