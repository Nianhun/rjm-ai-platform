package com.rjm.formulaai.management.persistence;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class AuthPersistenceConfig {
    @Bean
    public AuthRepository authRepository(
            DataSource dataSource,
            @Value("${rjm.auth.bootstrap-invite-code:RJM-BOOTSTRAP}") String bootstrapInviteCode) {
        return new AuthRepository(dataSource, bootstrapInviteCode);
    }

    @Bean
    public HistoryRepository historyRepository(DataSource dataSource, ObjectMapper objectMapper) {
        return new HistoryRepository(dataSource, objectMapper);
    }
}
